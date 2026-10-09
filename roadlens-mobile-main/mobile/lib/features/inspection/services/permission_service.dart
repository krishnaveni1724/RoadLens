import 'package:permission_handler/permission_handler.dart';

class PermissionCheckResult {
  const PermissionCheckResult({
    required this.allowed,
    this.cameraPermanentlyDenied = false,
    this.locationPermanentlyDenied = false,
    this.message,
  });

  final bool allowed;
  final bool cameraPermanentlyDenied;
  final bool locationPermanentlyDenied;
  final String? message;
}

class InspectionPermissionService {
  Future<PermissionCheckResult> ensureRequiredPermissions() async {
    var camera = await Permission.camera.status;
    if (camera.isDenied) camera = await Permission.camera.request();
    if (!camera.isGranted) {
      return PermissionCheckResult(
        allowed: false,
        cameraPermanentlyDenied:
            camera.isPermanentlyDenied || camera.isRestricted,
        message: 'Camera access is required to capture road damage.',
      );
    }

    var location = await Permission.locationWhenInUse.status;
    if (location.isDenied) {
      location = await Permission.locationWhenInUse.request();
    }
    if (!location.isGranted) {
      return PermissionCheckResult(
        allowed: false,
        locationPermanentlyDenied:
            location.isPermanentlyDenied || location.isRestricted,
        message: 'Location access is required for a road inspection.',
      );
    }
    return const PermissionCheckResult(allowed: true);
  }

  Future<bool> openSettings() => openAppSettings();
}
