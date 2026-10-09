import 'package:geolocator/geolocator.dart';

import '../domain/inspection.dart';

class RoadLensLocationService {
  Future<bool> isEnabled() => Geolocator.isLocationServiceEnabled();

  Future<bool> openSettings() => Geolocator.openLocationSettings();

  Future<GeoSnapshot> currentPosition() async {
    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 20),
      ),
    );
    return GeoSnapshot(
      latitude: position.latitude,
      longitude: position.longitude,
      accuracy: position.accuracy,
    );
  }
}
