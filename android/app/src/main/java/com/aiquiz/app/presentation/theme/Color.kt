package com.aiquiz.app.presentation.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

// Modern Vibrant Palette
val DeepIndigo = Color(0xFF0F172A)
val SurfaceDark = Color(0xFF1E293B)
val CardSurfaceDark = Color(0xFF334155)

val ElectricBlue = Color(0xFF38BDF8)
val VividIndigo = Color(0xFF6366F1)
val EmeraldGreen = Color(0xFF10B981)
val AmberOrange = Color(0xFFF59E0B)
val RoseRed = Color(0xFFF43F5E)

val TextPrimaryDark = Color(0xFFF8FAFC)
val TextSecondaryDark = Color(0xFF94A3B8)

val DarkColorScheme = darkColorScheme(
    primary = ElectricBlue,
    onPrimary = DeepIndigo,
    primaryContainer = VividIndigo,
    secondary = EmeraldGreen,
    background = DeepIndigo,
    surface = SurfaceDark,
    surfaceVariant = CardSurfaceDark,
    onSurface = TextPrimaryDark,
    onBackground = TextPrimaryDark
)

val LightColorScheme = lightColorScheme(
    primary = VividIndigo,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0E7FF),
    secondary = EmeraldGreen,
    background = Color(0xFFF8FAFC),
    surface = Color.White,
    surfaceVariant = Color(0xFFF1F5F9),
    onSurface = Color(0xFF0F172A),
    onBackground = Color(0xFF0F172A)
)
