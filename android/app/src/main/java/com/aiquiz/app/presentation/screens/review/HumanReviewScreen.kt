package com.aiquiz.app.presentation.screens.review

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.aiquiz.app.domain.model.Citation
import com.aiquiz.app.domain.model.Quiz
import com.aiquiz.app.presentation.components.CitationModal

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HumanReviewScreen(
    quiz: Quiz,
    onStartQuiz: () -> Unit,
    onNavigateHome: () -> Unit
) {
    var inspectingCitation by remember { mutableStateOf<Citation?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Human Review & Evidence", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateHome) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Home")
                    }
                }
            )
        },
        bottomBar = {
            Surface(
                shadowElevation = 8.dp,
                color = MaterialTheme.colorScheme.surface
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = onNavigateHome,
                        modifier = Modifier.weight(1f).height(50.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Save & Exit")
                    }
                    Button(
                        onClick = onStartQuiz,
                        modifier = Modifier.weight(1.5f).height(50.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Take Quiz Now")
                    }
                }
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(quiz.title, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Text(
                            "Review all generated questions, verified factual evidence, and citations below before testing yourself.",
                            fontSize = 13.sp,
                            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
                        )
                    }
                }
            }

            itemsIndexed(quiz.questions) { idx, q ->
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Question ${idx + 1}",
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                            SuggestionChip(
                                onClick = { inspectingCitation = q.source },
                                label = { Text("Citation: ${q.source.chunkId}") },
                                icon = { Icon(Icons.Default.CheckCircle, contentDescription = null, tint = Color(0xFF10B981), modifier = Modifier.size(16.dp)) }
                            )
                        }

                        Text(q.question, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)

                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            q.options.forEach { opt ->
                                val isCorrect = opt == q.correctAnswer
                                Surface(
                                    shape = RoundedCornerShape(8.dp),
                                    color = if (isCorrect) Color(0x3310B981) else MaterialTheme.colorScheme.surface,
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Row(
                                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            imageVector = if (isCorrect) Icons.Default.Check else Icons.Default.RadioButtonUnchecked,
                                            contentDescription = null,
                                            tint = if (isCorrect) Color(0xFF10B981) else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f),
                                            modifier = Modifier.size(16.dp)
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(opt, fontSize = 13.sp, fontWeight = if (isCorrect) FontWeight.Bold else FontWeight.Normal)
                                    }
                                }
                            }
                        }

                        Text(
                            text = "Explanation: ${q.explanation}",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                        )
                    }
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
