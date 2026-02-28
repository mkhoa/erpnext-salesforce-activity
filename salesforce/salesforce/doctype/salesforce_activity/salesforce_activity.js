frappe.ui.form.on('Salesforce Activity', {
	onload: function (frm) {
		if (frm.is_new() && !frm.doc.location) {
			// Auto capture GPS location on new document
			frappe.show_alert({ message: __('Fetching location automatically...'), indicator: 'blue' });

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
					frm.set_value('start_datetime', frappe.datetime.now_datetime());
					frappe.show_alert({ message: __('Location captured successfully!'), indicator: 'green' });
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
