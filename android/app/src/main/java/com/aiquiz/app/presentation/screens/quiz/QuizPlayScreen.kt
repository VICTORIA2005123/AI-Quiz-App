package com.aiquiz.app.presentation.screens.quiz

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.aiquiz.app.domain.model.Citation
import com.aiquiz.app.domain.model.Quiz
import com.aiquiz.app.presentation.components.CitationModal

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuizPlayScreen(
    quiz: Quiz,
    onFinishQuiz: (score: Int, total: Int) -> Unit,
    onNavigateBack: () -> Unit
) {
    var currentQuestionIndex by remember { mutableStateOf(0) }
    var selectedOption by remember { mutableStateOf<String?>(null) }
    var hasAnswered by remember { mutableStateOf(false) }
    var score by remember { mutableStateOf(0) }
    var inspectingCitation by remember { mutableStateOf<Citation?>(null) }

    val currentQuestion = quiz.questions.getOrNull(currentQuestionIndex)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Question ${currentQuestionIndex + 1}/${quiz.questions.size}", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.Close, contentDescription = "Exit")
                    }
                },
                actions = {
                    if (currentQuestion != null) {
                        IconButton(onClick = { inspectingCitation = currentQuestion.source }) {
                            Icon(Icons.Default.MenuBook, contentDescription = "View Evidence Citation", tint = MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            )
        }
    ) { padding ->
        if (currentQuestion == null) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No questions in this quiz.")
            }
            return@Scaffold
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(20.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Linear Progress Indicator
            LinearProgressIndicator(
                progress = { (currentQuestionIndex + 1).toFloat() / quiz.questions.size },
                modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.surfaceVariant
            )

            // Tags (Difficulty & Bloom Level)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SuggestionChip(
                    onClick = {},
                    label = { Text(currentQuestion.difficulty.uppercase()) }
                )
                SuggestionChip(
                    onClick = {},
                    label = { Text("Bloom: ${currentQuestion.bloomLevel.uppercase()}") }
                )
            }

            // Question Card
            Card(
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = currentQuestion.question,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(20.dp),
                    lineHeight = 26.sp
                )
            }

            // Options List
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                currentQuestion.options.forEach { option ->
                    val isSelected = selectedOption == option
                    val isCorrect = option == currentQuestion.correctAnswer

                    val bgColor by animateColorAsState(
                        when {
                            hasAnswered && isCorrect -> Color(0xFF10B981)
                            hasAnswered && isSelected && !isCorrect -> Color(0xFFEF4444)
                            isSelected -> MaterialTheme.colorScheme.primaryContainer
                            else -> MaterialTheme.colorScheme.surface
                        }, label = "optBg"
                    )

                    val textColor = when {
                        hasAnswered && (isCorrect || (isSelected && !isCorrect)) -> Color.White
                        isSelected -> MaterialTheme.colorScheme.onPrimaryContainer
                        else -> MaterialTheme.colorScheme.onSurface
                    }

                    Card(
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = bgColor),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable(enabled = !hasAnswered) {
                                selectedOption = option
                            }
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                imageVector = when {
                                    hasAnswered && isCorrect -> Icons.Default.CheckCircle
                                    hasAnswered && isSelected && !isCorrect -> Icons.Default.Cancel
                                    isSelected -> Icons.Default.RadioButtonChecked
                                    else -> Icons.Default.RadioButtonUnchecked
                                },
                                contentDescription = null,
                                tint = textColor
                            )
                            Text(
                                text = option,
                                fontSize = 15.sp,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                color = textColor,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }
                }
            }

            // Explanation & Citation if answered
            if (hasAnswered) {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Explanation", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(currentQuestion.explanation, fontSize = 13.sp)
                        Text(
                            text = "Source [${currentQuestion.source.chunkId}]: \"${currentQuestion.source.citation}\"",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // Action Button
            if (!hasAnswered) {
                Button(
                    onClick = {
                        if (selectedOption != null) {
                            hasAnswered = true
                            if (selectedOption == currentQuestion.correctAnswer) {
                                score += 1
                            }
                        }
                    },
                    enabled = selectedOption != null,
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Text("Submit Answer", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
            } else {
                Button(
                    onClick = {
                        if (currentQuestionIndex + 1 < quiz.questions.size) {
                            currentQuestionIndex += 1
                            selectedOption = null
                            hasAnswered = false
                        } else {
                            onFinishQuiz(score, quiz.questions.size)
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Text(
                        if (currentQuestionIndex + 1 < quiz.questions.size) "Next Question" else "View Results",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        if (inspectingCitation != null) {
            CitationModal(
                citation = inspectingCitation!!,
                onDismiss = { inspectingCitation = null }
            )
        }
    }
}
