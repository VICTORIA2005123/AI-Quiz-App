package com.aiquiz.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SourceCitationDto(
    @SerialName("chunk_id") val chunkId: String,
    @SerialName("citation") val citation: String,
    @SerialName("evidence_verified") val evidenceVerified: Boolean = true,
    @SerialName("confidence_score") val confidenceScore: Float = 1.0f
)

@Serializable
data class QuestionDto(
    @SerialName("question_id") val questionId: String,
    @SerialName("type") val type: String = "single_choice",
    @SerialName("question") val question: String,
    @SerialName("options") val options: List<String>,
    @SerialName("correct_answer") val correctAnswer: String,
    @SerialName("explanation") val explanation: String,
    @SerialName("difficulty") val difficulty: String = "medium",
    @SerialName("bloom_level") val bloomLevel: String = "understand",
    @SerialName("source") val source: SourceCitationDto
)

@Serializable
data class QuizDto(
    @SerialName("quiz_id") val quizId: String,
    @SerialName("title") val title: String,
    @SerialName("document_name") val documentName: String,
    @SerialName("difficulty") val difficulty: String,
    @SerialName("bloom_level") val bloomLevel: String,
    @SerialName("question_count") val questionCount: Int,
    @SerialName("questions") val questions: List<QuestionDto>,
    @SerialName("created_at") val createdAt: String
)

@Serializable
data class JobStatusDto(
    @SerialName("job_id") val jobId: String,
    @SerialName("status") val status: String,
    @SerialName("current_step") val currentStep: String,
    @SerialName("progress_percentage") val progressPercentage: Int,
    @SerialName("error_message") val errorMessage: String? = null,
    @SerialName("quiz") val quiz: QuizDto? = null,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
data class TokenResponseDto(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    @SerialName("token_type") val tokenType: String = "bearer",
    @SerialName("expires_in_minutes") val expiresInMinutes: Int
)

@Serializable
data class QuotaResponseDto(
    @SerialName("daily_used") val dailyUsed: Int,
    @SerialName("daily_limit") val dailyLimit: Int,
    @SerialName("daily_remaining") val dailyRemaining: Int,
    @SerialName("active_concurrent") val activeConcurrent: Int,
    @SerialName("max_concurrent") val maxConcurrent: Int
)
