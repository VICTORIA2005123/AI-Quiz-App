package com.aiquiz.app.presentation.navigation

import androidx.compose.runtime.*
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.aiquiz.app.data.local.EncryptedPreferencesManager
import com.aiquiz.app.data.repository.QuizRepositoryImpl
import com.aiquiz.app.domain.model.JobProgress
import com.aiquiz.app.domain.model.Quiz
import com.aiquiz.app.presentation.screens.create.CreateQuizScreen
import com.aiquiz.app.presentation.screens.home.HomeScreen
import com.aiquiz.app.presentation.screens.progress.JobProgressScreen
import com.aiquiz.app.presentation.screens.quiz.QuizPlayScreen
import com.aiquiz.app.presentation.screens.results.QuizResultScreen
import com.aiquiz.app.presentation.screens.review.HumanReviewScreen
import com.aiquiz.app.presentation.screens.settings.SettingsScreen
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Create : Screen("create")
    object Progress : Screen("progress")
    object HumanReview : Screen("human_review")
    object Play : Screen("play")
    object Result : Screen("result")
    object Settings : Screen("settings")
}

@Composable
fun AppNavGraph(
    navController: NavHostController,
    repository: QuizRepositoryImpl,
    prefs: EncryptedPreferencesManager
) {
    val coroutineScope = rememberCoroutineScope()
    val quizzes by repository.getLocalQuizzes().collectAsState(initial = emptyList())

    var activeJobProgress by remember { mutableStateOf<JobProgress?>(null) }
    var selectedQuiz by remember { mutableStateOf<Quiz?>(null) }
    var lastScore by remember { mutableStateOf(0) }
    var lastTotal by remember { mutableStateOf(0) }
    var isHumanReviewMode by remember { mutableStateOf(false) }

    NavHost(navController = navController, startDestination = Screen.Home.route) {
        composable(Screen.Home.route) {
            HomeScreen(
                quizzes = quizzes,
                onNavigateToCreate = { navController.navigate(Screen.Create.route) },
                onNavigateToQuiz = { quiz ->
                    selectedQuiz = quiz
                    navController.navigate(Screen.Play.route)
                },
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
            )
        }

        composable(Screen.Create.route) {
            CreateQuizScreen(
                onNavigateBack = { navController.popBackStack() },
                onSubmitJob = { file, count, diff, bloom, pii, humanReview ->
                    isHumanReviewMode = humanReview
                    coroutineScope.launch {
                        navController.navigate(Screen.Progress.route)
                        val result = repository.submitDocumentJob(file, count, diff, bloom, pii, true)
                        result.onSuccess { progress ->
                            activeJobProgress = progress
                            // Start polling loop
                            while (activeJobProgress?.status !in listOf("COMPLETED", "FAILED", "CANCELLED")) {
                                delay(1200)
                                val pollResult = repository.pollJobStatus(progress.jobId)
                                pollResult.onSuccess { updated ->
                                    activeJobProgress = updated
                                }
                            }
                        }.onFailure { error ->
                            activeJobProgress = JobProgress(
                                jobId = "error",
                                status = "FAILED",
                                currentStep = "Upload failed",
                                progressPercentage = 0,
                                errorMessage = error.message
                            )
                        }
                    }
                }
            )
        }

        composable(Screen.Progress.route) {
            JobProgressScreen(
                jobProgress = activeJobProgress,
                onCancelJob = {
                    val jId = activeJobProgress?.jobId
                    if (jId != null) {
                        coroutineScope.launch {
                            repository.cancelJob(jId)
                        }
                    }
                },
                onQuizReady = { quiz ->
                    selectedQuiz = quiz
                    navController.navigate(Screen.Play.route) {
                        popUpTo(Screen.Home.route)
                    }
                },
                onReviewReady = { quiz ->
                    selectedQuiz = quiz
                    navController.navigate(Screen.HumanReview.route) {
                        popUpTo(Screen.Home.route)
                    }
                },
                isHumanReviewMode = isHumanReviewMode
            )
        }

        composable(Screen.HumanReview.route) {
            if (selectedQuiz != null) {
                HumanReviewScreen(
                    quiz = selectedQuiz!!,
                    onStartQuiz = {
                        navController.navigate(Screen.Play.route)
                    },
                    onNavigateHome = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Home.route) { inclusive = true }
                        }
                    }
                )
            }
        }

        composable(Screen.Play.route) {
            if (selectedQuiz != null) {
                QuizPlayScreen(
                    quiz = selectedQuiz!!,
                    onFinishQuiz = { score, total ->
                        lastScore = score
                        lastTotal = total
                        navController.navigate(Screen.Result.route) {
                            popUpTo(Screen.Home.route)
                        }
                    },
                    onNavigateBack = { navController.popBackStack() }
                )
            }
        }

        composable(Screen.Result.route) {
            QuizResultScreen(
                score = lastScore,
                totalQuestions = lastTotal,
                onRetry = {
                    navController.navigate(Screen.Play.route) {
                        popUpTo(Screen.Home.route)
                    }
                },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                prefs = prefs,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
