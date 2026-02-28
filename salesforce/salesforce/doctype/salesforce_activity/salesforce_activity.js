frappe.ui.form.on('Salesforce Activity', {
	onload(frm) {
		// Auto-fill Sales Person for new documents only
		if (frm.is_new() && !frm.doc.sales_person) {
			frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name', (r) => {
				if (r?.name) {
					frappe.db.get_value('Sales Person', { employee: r.name }, 'name', (r2) => {
						if (r2?.name && !frm.doc.sales_person) {
							frm.set_value('sales_person', r2.name);
						}
					});
				}
			});
		}

		// Auto-capture GPS whenever document is in Draft state (includes new docs)
		if (frm.doc.docstatus === 0) {
			capture_location(frm);
		}
	},

	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			if (frm.doc.status !== "Closed" && frm.doc.status !== "Cancelled") {
				frm.add_custom_button(__('Close'), () => frm.events.update_status(frm, 'Closed'), __('Status'));
			} else if (frm.doc.status === "Closed") {
				frm.add_custom_button(__('Re-open'), () => frm.events.update_status(frm, 'Open'), __('Status'));
			}
		}
	},

	update_status(frm, status) {
		frappe.call({
			method: 'salesforce.salesforce.doctype.salesforce_activity.salesforce_activity.update_status',
			args: {
				name: frm.doc.name,
				status: status
			},
			callback: function (r) {
				if (!r.exc) {
					frappe.show_alert({ message: __('Activity ' + status), indicator: 'green' });
					frm.reload_doc();
				}
			}
		});
	}
});

function capture_location(frm) {
	if (!navigator.geolocation) {
		frappe.msgprint(__('Geolocation is not supported by this browser/device.'));
		return;
	}

	frappe.show_alert({ message: __('Fetching current location...'), indicator: 'blue' });

	navigator.geolocation.getCurrentPosition(
		(position) => {
			const location_json = {
				type: 'FeatureCollection',
				features: [{
					type: 'Feature',
					properties: {},
					geometry: {
						type: 'Point',
						coordinates: [position.coords.longitude, position.coords.latitude]
					}
				}]
			};
			frm.set_value('location', JSON.stringify(location_json));

			// Only set start_datetime if it's empty, to avoid overwriting planned times
			if (!frm.doc.start_datetime) {
				frm.set_value('start_datetime', frappe.datetime.now_datetime());
			}

			frappe.show_alert({ message: __('Location updated successfully!'), indicator: 'green' });
		},
		(error) => {
			frappe.msgprint(__('Error capturing location: ') + error.message);
		},
		{ enableHighAccuracy: true }
	);
}

