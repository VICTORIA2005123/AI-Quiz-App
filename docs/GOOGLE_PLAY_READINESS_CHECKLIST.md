# Google Play Production-Readiness Checklist & Compliance Guide

This document specifies the technical configurations, Play Console Data Safety entries, and compliance requirements to ensure **AI Quiz Master** passes Google Play Store production reviews.

---

## 1. Google Play Data Safety Declaration Mapping

| Question on Play Console | App Specification & Declaration |
| :--- | :--- |
| **Does your app collect or share user data?** | **Yes** (User email for account creation/authentication, Ephemeral document files). |
| **Is data encrypted in transit?** | **Yes** — All network communications enforce TLS 1.3 / HTTPS via strict `network_security_config.xml`. |
| **Do you provide a way for users to request data deletion?** | **Yes** — In-app account/quiz purge and server-side ephemeral shredding. |
| **User Documents & Files:** | **Ephemeral Document Processing**: Documents are transferred securely over HTTPS to the backend, parsed in memory/temp RAM, used to extract quizzes, and **permanently wiped/shredded immediately upon job completion**. Raw text is **NEVER** stored in persistent databases. |
| **Generative AI Transparency:** | Grounded AI generator; content is strictly sourced and cited from user-provided educational material. |

---

## 2. Android 15 & 16KB Page Size Alignment

To comply with Google Play's 16KB memory page size alignment requirement for Android 15+:
- The app uses pure Kotlin and standard NDK-free dependencies (Jetpack Compose, Room, Retrofit, OkHttp, AndroidX Security).
- Gradle build configuration targets `compileSdk = 35` and `targetSdk = 35`.
- Dynamic libraries in native packaging (if added later) are verified with:
  ```bash
  llvm-objdump -p <path_to_so> | grep LOAD
  ```

---

## 3. Edge-to-Edge & Modern UI Compliance

- **Edge-to-Edge Display**: Handled via `enableEdgeToEdge()` in `MainActivity.kt` with transparent system bars.
- **Predictive Back Navigation**: Fully compatible with Android 14/15 back gesture dispatcher.
- **Biometric Security UX**: Biometric authentication (`BiometricPrompt`) is provided as an **optional user-facing privacy toggle** in Settings rather than a mandatory blockage.

---

## 4. App Signing & Keystore Management

For Play Console upload:
1. Generate an upload key using Android Studio:
   ```bash
   keytool -genkey -v -keystore release-upload-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   ```
2. Build Android App Bundle (.aab):
   ```bash
   ./gradlew bundleRelease
   ```
3. Enable **Play App Signing** in the Play Console to let Google manage distribution keys.

---

## 5. Security & ProGuard / R8 Hardening

The app includes production-tested `proguard-rules.pro` that:
- Obfuscates business logic and use cases
- Retains reflection-safe models for `@kotlinx.serialization.Serializable`
- Keeps Room Database DAOs and entities
- Retains Retrofit endpoints
- Enforces certificate pinning / disables cleartext traffic via `network_security_config.xml`
