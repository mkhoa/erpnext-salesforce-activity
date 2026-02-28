frappe.ui.form.on('Salesforce Activity', {
	onload: function (frm) {
		if (frm.is_new()) {
			// Auto-fill Sales Person based on current user
			if (!frm.doc.sales_person) {
				frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name', (r) => {
					if (r && r.name && !frm.doc.sales_person) {
						frappe.db.get_value('Sales Person', { employee: r.name }, 'name', (r2) => {
							if (r2 && r2.name) {
								frm.set_value('sales_person', r2.name);
							}
						});
					}
				});
			}
		}

		// Auto capture GPS location if document is Draft (docstatus == 0) or New
		if (frm.doc.docstatus === 0 || frm.is_new()) {
			frappe.show_alert({ message: __('Fetching current location...'), indicator: 'blue' });

			if (navigator.geolocation) {
				navigator.geolocation.getCurrentPosition(function (position) {
					const location_json = {
						"type": "FeatureCollection",
						"features": [
							{
								"type": "Feature",
								"properties": {},
								"geometry": {
									"type": "Point",
									"coordinates": [position.coords.longitude, position.coords.latitude]
								}
							}
						]
					};
					frm.set_value('location', JSON.stringify(location_json));

					// Only set start_datetime if it's currently empty, to avoid overwriting planned times
					if (!frm.doc.start_datetime) {
						frm.set_value('start_datetime', frappe.datetime.now_datetime());
					}

					frappe.show_alert({ message: __('Location updated successfully!'), indicator: 'green' });
				}, function (error) {
					frappe.msgprint(__('Error capturing location: ') + error.message);
				}, {
					enableHighAccuracy: true
				});
			} else {
				frappe.msgprint(__('Geolocation is not supported by this browser/device.'));
			}
		}
	}
});
