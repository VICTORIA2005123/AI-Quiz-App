package com.aiquiz.app.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

enum class StepState {
    PENDING, ACTIVE, COMPLETED
}

@Composable
fun ProgressStepItem(
    title: String,
    state: StepState,
    isLast: Boolean = false
) {
    val iconBgColor by animateColorAsState(
        when (state) {
            StepState.COMPLETED -> Color(0xFF10B981)
            StepState.ACTIVE -> MaterialTheme.colorScheme.primary
            StepState.PENDING -> MaterialTheme.colorScheme.surfaceVariant
        }, label = "stepColor"
    )

    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .background(iconBgColor)
        ) {
            when (state) {
                StepState.COMPLETED -> {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(18.dp)
                    )
                }
                StepState.ACTIVE -> {
                    CircularProgressIndicator(
                        color = Color.White,
                        strokeWidth = 2.dp,
                        modifier = Modifier.size(16.dp)
                    )
                }
                StepState.PENDING -> {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f))
                    )
                }
            }
        }

        Text(
            text = title,
            fontSize = 15.sp,
            fontWeight = if (state == StepState.ACTIVE) FontWeight.Bold else FontWeight.Normal,
            color = if (state == StepState.PENDING) MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f) else MaterialTheme.colorScheme.onSurface
        )
    }
}
