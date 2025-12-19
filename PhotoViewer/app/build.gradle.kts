plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.photoviewer"
    compileSdk = 36   // ✅ 必须 >= 36 才能兼容 androidx.activity:1.11.0

    defaultConfig {
        applicationId = "com.example.photoviewer"
        minSdk = 26     // ✅ 建议不要设太高（33 会导致低版本手机无法运行）
        targetSdk = 36  // ✅ 同步到 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildToolsVersion = "36.0.0"

    // ✅ 可选：若项目有 Kotlin 源码，可启用以下块
    // kotlinOptions {
    //     jvmTarget = "11"
    // }
}

dependencies {
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}
