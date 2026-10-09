import java.io.FileInputStream
import java.util.Properties

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

val signingPropertiesPath = System.getenv("ROADLENS_SIGNING_PROPERTIES")
val signingKeystorePath = System.getenv("ROADLENS_KEYSTORE_PATH")
val signingProperties = Properties()
val signingPropertiesFile = signingPropertiesPath?.let(::file)
val hasReleaseSigning = signingPropertiesFile?.isFile == true &&
    !signingKeystorePath.isNullOrBlank() && file(signingKeystorePath).isFile

if (hasReleaseSigning) {
    FileInputStream(signingPropertiesFile).use(signingProperties::load)
}

val requiredSigningProperties = listOf("storePassword", "keyPassword", "keyAlias")
val releaseTaskRequested = gradle.startParameter.taskNames.any {
    it.contains("release", ignoreCase = true)
}

if (releaseTaskRequested && (!hasReleaseSigning || requiredSigningProperties.any {
        signingProperties.getProperty(it).isNullOrBlank()
    })) {
    throw GradleException(
        "Release signing is not configured. Set ROADLENS_SIGNING_PROPERTIES and " +
            "ROADLENS_KEYSTORE_PATH to client-owned files outside the repository.",
    )
}

android {
    namespace = "com.roadlens.roadlens"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.roadlens.roadlens"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = 24
        targetSdk = flutter.targetSdkVersion
        // Uses the version code from pubspec.yaml. When using split APKs, 1000 * ABI_VERSION
        // is added automatically by Flutter. (https://developer.android.com/studio/build/configure-apk-splits#configure-APK-versions)
        // You can force using the value of versionCode by specifying the `-P force-version-code-ignoring-abi=true`
        // flag during build.
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("release") {
                keyAlias = signingProperties.getProperty("keyAlias")
                keyPassword = signingProperties.getProperty("keyPassword")
                storeFile = file(signingKeystorePath!!)
                storePassword = signingProperties.getProperty("storePassword")
            }
        }
    }

    buildTypes {
        release {
            if (hasReleaseSigning) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
