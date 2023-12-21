console.log("Welcome to pymaplibregl!")

/*
if (Shiny) {
	console.log("Shiny");
	Shiny.addCustomMessageHandler("maplibregl", (payload) => {
		console.log(payload);
	});
}
*/

if (Shiny) {
  class MapLibreGLOutputBinding extends Shiny.OutputBinding {
    find(scope) {
        console.log("I am here!");
        return scope.find(".shiny-maplibregl-output");
    }

    renderValue(el, payload) {
        console.log(el.id, payload);
        const params = Object.assign({container: el.id}, payload.data.mapOptions)
        this.map = new maplibregl.Map(params)
        this.map.on("load", () => payload.data.markers.forEach(({lngLat, popup, options}) => {
            console.log(lngLat, popup, options);
             const marker = new maplibregl.Marker(options).setLngLat(lngLat);
             if (popup) {
                 const popup_ = new maplibregl.Popup().setText(popup);
                 marker.setPopup(popup_);
             }
             marker.addTo(this.map);
        }));
    }
  }

  Shiny.outputBindings.register(
      new MapLibreGLOutputBinding(),
      "shiny-maplibregl-output"
  );
}
