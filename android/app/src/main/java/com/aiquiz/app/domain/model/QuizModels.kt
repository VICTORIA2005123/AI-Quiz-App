package com.aiquiz.app.domain.model

data class Citation(
    val chunkId: String,
    val citation: String,
    val evidenceVerified: Boolean = true,
    val confidenceScore: Float = 1.0f
)

data class Question(
    val questionId: String,
    val type: String,
    val question: String,
    val options: List<String>,
    val correctAnswer: String,
    val explanation: String,
    val difficulty: String,
    val bloomLevel: String,
    val source: Citation
)

data class Quiz(
    val quizId: String,
    val title: String,
    val documentName: String,
    val difficulty: String,
    val bloomLevel: String,
    val questionCount: Int,
    val questions: List<Question>,
    val createdAt: String
)

data class JobProgress(
    val jobId: String,
    val status: String,
    val currentStep: String,
    val progressPercentage: Int,
    val errorMessage: String? = null,
    val quiz: Quiz? = null
)
