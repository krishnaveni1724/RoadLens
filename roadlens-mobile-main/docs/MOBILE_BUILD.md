# RoadLens mobile build

## Requirements

- Flutter 3.47.1 (stable) with Dart 3.13.1 or a compatible newer stable release
- Android SDK with API 36, Build Tools 36.0.0, NDK 28.2.13676358, and CMake 3.22.1
- JDK 17

## Configure the API

RoadLens reads `APP_ENV` and `API_BASE_URL` from Dart compile-time defines. Production mode refuses non-HTTPS URLs. Do not use `localhost` or `127.0.0.1` on Android.

Android emulator development build:

```powershell
flutter pub get
flutter run --dart-define=APP_ENV=development --dart-define=API_BASE_URL=http://10.0.2.2:4173
```

Physical-device development build (replace the address with the developer PC's LAN address and allow the backend through the firewall):

```powershell
flutter run --dart-define=APP_ENV=development --dart-define=API_BASE_URL=http://192.168.1.20:4173
```

Production release build:

```powershell
flutter pub get
flutter analyze
flutter test
$env:ROADLENS_SIGNING_PROPERTIES='C:\secure\roadlens-signing.properties'
$env:ROADLENS_KEYSTORE_PATH='C:\secure\roadlens-release.jks'
flutter build apk --release --dart-define=APP_ENV=production --dart-define=API_BASE_URL=https://roadlens-api.onrender.com
```

The APK is written to `mobile/build/app/outputs/flutter-apk/app-release.apk`.

## Signing

Release tasks require a client-owned keystore and an external Java-properties file containing `storePassword`, `keyPassword`, and `keyAlias`. Set `ROADLENS_KEYSTORE_PATH` and `ROADLENS_SIGNING_PROPERTIES` to those files before building. Gradle fails a release task when either file or a required value is missing, preventing accidental debug signing. Keep both files outside source control and never commit passwords or private keys.

## Runtime behavior

- Camera and foreground location permissions are requested sequentially.
- Location services must be enabled and a real non-zero location acquired before capture.
- The capture-time timestamp is timezone-aware.
- The captured image is saved before upload.
- If the API is unavailable, the record stays in Drift/SQLite as `ANALYSIS_PENDING`; the connectivity listener retries pending inspections.
- Authentication is intentionally not simulated: the inspected backend exposes no authentication API, so the login screen clearly offers local mode and no passwords/tokens are stored.

## Production checklist

1. Deploy the backend at a stable HTTPS URL.
2. Replace the default Flutter launcher icon with the client-approved RoadLens artwork.
3. Configure client-owned release signing.
4. Build with `APP_ENV=production` and the deployed HTTPS URL.
5. Install that artifact on a physical Android phone and complete the camera/GPS/backend flow.
