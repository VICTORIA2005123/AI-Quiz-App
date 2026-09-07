package com.aiquiz.app.presentation

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.aiquiz.app.AIQuizApplication
import com.aiquiz.app.core.security.BiometricAuthHelper
import com.aiquiz.app.data.remote.NetworkClient
import com.aiquiz.app.data.repository.QuizRepositoryImpl
import com.aiquiz.app.presentation.navigation.AppNavGraph
import com.aiquiz.app.presentation.theme.AIQuizTheme

class MainActivity : ComponentActivity() {

    private var onDocumentSelectedCallback: ((Uri?) -> Unit)? = null

    private val documentPickerLauncher: ActivityResultLauncher<Array<String>> =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
            onDocumentSelectedCallback?.invoke(uri)
        }

    fun launchDocumentPicker(onFileSelected: (Uri?) -> Unit) {
        onDocumentSelectedCallback = onFileSelected
        val supportedMimeTypes = arrayOf(
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/plain",
            "text/markdown",
            "text/csv",
            "text/html",
            "image/*"
        )
        documentPickerLauncher.launch(supportedMimeTypes)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = application as AIQuizApplication
        val prefs = app.encryptedPreferences
        val db = app.database
        val apiService = NetworkClient.createApiService(prefs)
        val repository = QuizRepositoryImpl(apiService, db.quizDao())
        val biometricHelper = BiometricAuthHelper(this)

        setContent {
            AIQuizTheme {
                var isUnlocked by remember { mutableStateOf(!prefs.isBiometricEnabled()) }

                if (!isUnlocked && prefs.isBiometricEnabled() && biometricHelper.isBiometricAvailable()) {
                    biometricHelper.promptBiometric(
                        onSuccess = { isUnlocked = true },
                        onError = { /* fallback */ }
                    )
                }

                Surface(modifier = Modifier.fillMaxSize()) {
                    val navController = rememberNavController()
                    AppNavGraph(
                        navController = navController,
                        repository = repository,
                        prefs = prefs
                    )
                }
            }
        }
    }
}
