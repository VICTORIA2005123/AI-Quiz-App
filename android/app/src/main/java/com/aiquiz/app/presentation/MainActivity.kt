package com.aiquiz.app.presentation

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.fragment.app.FragmentActivity
import androidx.navigation.compose.rememberNavController
import com.aiquiz.app.AIQuizApplication
import com.aiquiz.app.core.security.BiometricAuthHelper
import com.aiquiz.app.data.remote.NetworkClient
import com.aiquiz.app.data.repository.QuizRepositoryImpl
import com.aiquiz.app.presentation.navigation.AppNavGraph
import com.aiquiz.app.presentation.theme.AIQuizTheme

class MainActivity : FragmentActivity() {

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
