package com.aiquiz.app.presentation.screens.progress

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.aiquiz.app.domain.model.JobProgress
import com.aiquiz.app.domain.model.Quiz
import com.aiquiz.app.presentation.components.ProgressStepItem
import com.aiquiz.app.presentation.components.StepState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JobProgressScreen(
    jobProgress: JobProgress?,
    onCancelJob: () -> Unit,
    onQuizReady: (Quiz) -> Unit,
    onReviewReady: (Quiz) -> Unit,
    isHumanReviewMode: Boolean
) {
    val status = jobProgress?.status ?: "QUEUED"
    val progress = jobProgress?.progressPercentage ?: 0
    val currentStep = jobProgress?.currentStep ?: "Initializing..."

    LaunchedEffect(jobProgress) {
        if (status == "COMPLETED" && jobProgress?.quiz != null) {
            if (isHumanReviewMode) {
                onReviewReady(jobProgress.quiz)
            } else {
                onQuizReady(jobProgress.quiz)
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Processing Document", fontWeight = FontWeight.Bold) }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Spacer(modifier = Modifier.height(10.dp))

            // Progress Radial Indicator
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier.size(140.dp)
            ) {
                CircularProgressIndicator(
                    progress = { progress / 100f },
                    strokeWidth = 10.dp,
                    color = MaterialTheme.colorScheme.primary,
                    trackColor = MaterialTheme.colorScheme.surfaceVariant,
                    modifier = Modifier.fillMaxSize()
                )
                Text(
                    text = "$progress%",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = currentStep,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "Status: $status",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }

            // Explicit Stepper Progression
            Card(
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    ProgressStepItem(
                        title = "File Security & Magic Bytes Verified",
                        state = getStepState(progress, 10)
                    )
                    ProgressStepItem(
                        title = "Text Extracted & Normalized",
                        state = getStepState(progress, 30)
                    )
                    ProgressStepItem(
                        title = "Semantic Chunks & Anchors Generated",
                        state = getStepState(progress, 50)
                    )
                    ProgressStepItem(
                        title = "Educational PII Protected",
                        state = getStepState(progress, 60)
                    )
                    ProgressStepItem(
                        title = "Grounded AI Quiz Generated",
                        state = getStepState(progress, 80)
                    )
                    ProgressStepItem(
                        title = "Evidence Verified & Factual Audit",
                        state = getStepState(progress, 95),
                        isLast = true
                    )
                }
            }

            if (status == "FAILED") {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Error, contentDescription = null, tint = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = jobProgress?.errorMessage ?: "An error occurred during processing.",
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            if (status != "COMPLETED" && status != "FAILED") {
                OutlinedButton(
                    onClick = onCancelJob,
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error),
                    modifier = Modifier.fillMaxWidth().height(50.dp)
                ) {
                    Icon(Icons.Default.Close, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Cancel Processing", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

private fun getStepState(currentProgress: Int, stepThreshold: Int): StepState {
    return when {
        currentProgress > stepThreshold -> StepState.COMPLETED
        currentProgress == stepThreshold -> StepState.ACTIVE
        else -> StepState.PENDING
    }
}
