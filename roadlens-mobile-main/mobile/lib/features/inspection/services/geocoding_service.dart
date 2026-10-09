import 'package:geocoding/geocoding.dart';

class RoadLensGeocodingService {
  Future<String?> reverse(double latitude, double longitude) async {
    try {
      final places = await Geocoding().placemarkFromCoordinates(
        latitude,
        longitude,
      );
      if (places.isEmpty) return null;
      final place = places.first;
      final values = <String?>[
        place.street,
        place.locality,
        place.subAdministrativeArea,
        place.administrativeArea,
        place.postalCode,
        place.country,
      ];
      final unique = <String>[];
      for (final value in values) {
        final cleaned = value?.trim();
        if (cleaned != null &&
            cleaned.isNotEmpty &&
            !unique.contains(cleaned)) {
          unique.add(cleaned);
        }
      }
      return unique.isEmpty ? null : unique.join(', ');
    } catch (_) {
      return null;
    }
  }
}
