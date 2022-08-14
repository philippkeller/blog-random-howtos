---
title: How to create a map in mapbox for flutter
date: 2022-08-01 08:27:49
tags:
---

![](/images/mapbox.png)

[Mapbox for flutter](https://pub.dev/packages/mapbox_gl) is still not documented well enough. I've spent almost a day until I had something working. With this blog post I hope to help the next ones, so that they don't need so much time setting it up.

<!-- more -->

## Adding the dependency

I *thought* it would be done with `flutter pub add mapbox_gl` and `flutter pub get`, but it was not. For iOS, the compiling process choked at `pod install` time:

```
[!] Error installing Mapbox-iOS-SDK
curl: (22) The requested URL returned error: 401 Unauthorized
```

And for Android it also didn't work.

In hindsight, I should have read the docs better, because [they cover the following steps](https://docs.mapbox.com/ios/maps/guides/install/#configure-credentials):

1. Go to [your mapbox account](https://account.mapbox.com/access-tokens/)
2. Click `+ Create token`
3. Give it a name
4. Check the `Downloads:Read` checkbox
5. Generate the token and copy the secret to a safe place

### iOS

Create the file `~/.netrc` and put the following into it:


```
machine api.mapbox.com
login mapbox
password YOUR_SECRET_MAPBOX_ACCESS_TOKEN
```

Now, `pod install` should work.


### Android

Of course, Android building takes the access token from somewhere else :) Put this into `~/.gradle/gradle.properties`:

```
MAPBOX_DOWNLOADS_TOKEN=YOUR_SECRET_MAPBOX_ACCESS_TOKEN
```

## Running on the iOS simulator

Now it should all work, right? Except it doesn't. When doing the Xcode build then I ran into:

```
ld: building for iOS Simulator, but linking in dylib built for iOS, file '/Users/username/code/appname/ios/Pods/Mapbox-iOS-SDK/dynamic/Mapbox.framework/Mapbox' for architecture arm64
```

This seems to be only a problem when debugging on iOS simulator. [This stackoverflow answer](https://stackoverflow.com/a/63955114/119861) helped me solving it. In your `ios/Podfile` you need to add the following:

```
post_install do |installer|
  installer.pods_project.build_configurations.each do |config|
    config.build_settings["EXCLUDED_ARCHS[sdk=iphonesimulator*]"] = "arm64"
  end
end
```

Since I already had a section with `post_install do |installer|` I needed to append it to the end so for me this now looks like this:

```
post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
  end
  installer.pods_project.build_configurations.each do |config|
    config.build_settings["EXCLUDED_ARCHS[sdk=iphonesimulator*]"] = "arm64"
  end
end
```

But now it should work? Still not! 😱 When I started the app in the iOS simulator, it immediately crashed. I needed to add follow [this stackoverflow advice](https://stackoverflow.com/a/72401837/119861):

Add the following lines into `<dict>` of your `ios/Runner/Info.plist`:

```
<key>io.flutter.embedded_views_preview</key>
<true/>
<key>MGLMapboxMetricsEnabledSettingShownInApp</key>
<true/>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Shows your location on the map and helps improve the map</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>Shows your location on the map and helps improve the map</string>
```

And then run:

1. `flutter clean`
2. `flutter create . --project-name my-project-name`

But **take care**! The last command (not sure if it is needed at all?) created for me `android/app/src/main/kotlin/ch/weegee/MainActivity.kt` which was then later causing trouble for my Android build so I needed to remove that file again.

And now, finally, it worked for me for both iOS and Android.

## A minimal example

Here's a minimal example which shows a map in full page with a marker:


```
import 'package:mapbox_gl/mapbox_gl.dart';
import 'package:flutter/material.dart';

import '../models/mapbox_api.dart';

class MapDetails extends StatelessWidget {
  final LatLng latLng;
  const MapDetails({Key? key, required this.latLng}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: MapboxMap(
        initialCameraPosition: CameraPosition(
          target: latLng,
          zoom: 13,
        ),
        onMapCreated: (controller) => addMarker(controller, latLng),
        accessToken: mapboxPublicToken,
      ),
    );
  }
}

void addMarker(MapboxMapController controller, LatLng latLng) async {
  var byteData = await rootBundle.load("images/poi.png");
  var markerImage = byteData.buffer.asUint8List();

  controller.addImage('marker', markerImage);

  await controller.addSymbol(
    SymbolOptions(
      iconSize: 0.3,
      iconImage: "marker",
      geometry: latLng,
      iconAnchor: "bottom",
    ),
  );
}
```


A few remarks:

- I had no luck with the "built in" markers. [This](https://labs.mapbox.com/maki-icons/) should be the list of supported markers but I couldn't get them to work
- <a href="/images/poi.png">images/poi.png</a> in my case is just a 256x256 PNG image with transparent background
- iconMarker tells how to position the marker. In my case it is kind of a pin icon <img src="/images/poi.png" style="display: inline-block; float: none; padding: 0" width="30" /> so I want the "center bottom" to be where the lat/lng is
- iconSize you need to find out the best size. In my case I needed to hot restart every time I did a change which was annoying…
- `mapboxPublicToken` is the public token. In the [flutter mapbox documentation they advice to not store it in source code](https://pub.dev/packages/mapbox_gl#all-platforms) but since the token is public anyway when using it for web, and for mobile you can just unzip the APK and then have the token as well. Plus it's a "public" token I don't see the point securing it into an environment variable, so I just store it in source code.

If you want to have the mapbox tile part of a screen (i.e. not filling the whole screen) you probably will have it as child of a `column`. To not run into the `Horizontal viewport was given unbounded height` exception, you need to limit it's height:

```
Column(
  children: [
    …,
		Padding(
		  padding: const EdgeInsets.symmetric(horizontal: 15),
		  child: Center(
		    child: SizedBox(
		      width: double.infinity,
		      height: 150,
		      child: MapboxMap(
		        onMapCreated: (controller) =>
		            this.controller = controller,
		        onStyleLoadedCallback: () =>
		            addMarker(controller!, latLng!),
		        initialCameraPosition: CameraPosition(
		          target: latLng!,
		          zoom: 13,
		        ),
		        accessToken: mapboxPublicToken,
		      ),
		    ),
		  ),
		),
		…,
	]
)
```

You might notice that here the marker is loaded only at `onStyleLoadedCallback`. I needed to move it to this, since I ran into some nullpointer issues when adding the marker with `onMapCreated`.

Now, on Android I had the issue that the map was showing top left of the screen. There is [this currently open issue](https://github.com/flutter-mapbox-gl/maps/issues/1125) - which at the time you're reading might be closed already. If it isn't: I was able to resolve this downgrading to version `0.14.0`.

That's it. As always: I hope I covered all the issues I had. If I missed something, please use the comments.