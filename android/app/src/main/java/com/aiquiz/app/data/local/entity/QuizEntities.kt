package com.aiquiz.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ForeignKey
import androidx.room.Index

@Entity(tableName = "local_quizzes")
data class QuizEntity(
    @PrimaryKey
    val id: String,
    val title: String,
    val documentName: String,
    val difficulty: String,
    val bloomLevel: String,
    val questionCount: Int,
    val createdAtEpoch: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "local_questions",
    foreignKeys = [
        ForeignKey(
            entity = QuizEntity::class,
            parentColumns = ["id"],
            childColumns = ["quizId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("quizId")]
)
data class QuestionEntity(
    @PrimaryKey
    val id: String,
    val quizId: String,
    val questionType: String,
    val questionText: String,
    val optionsJson: String,
    val correctAnswer: String,
    val explanation: String,
    val difficulty: String,
    val bloomLevel: String,
    val sourceChunkId: String,
    val citationQuote: String,
    val evidenceVerified: Boolean,
    val confidenceScore: Float
)
