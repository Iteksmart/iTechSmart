import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

export default function AnalysisScreen({ route, navigation }) {
  const { photoUri } = route.params;
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    analyzeOutfit();
  }, []);

  const analyzeOutfit = async () => {
    // Simulate API call
    setTimeout(() => {
      setAnalysis({
        style_score: 8.7,
        color_harmony: 9.2,
        trend_match: 8.5,
        overall_rating: 8.8,
        detected_items: ['Top', 'Jeans', 'Sneakers', 'Watch'],
        colors: ['#2C3E50', '#3498DB', '#FFFFFF', '#E74C3C'],
        style_category: 'Casual Chic',
        feedback: [
          '✨ Great color coordination!',
          '👍 The denim pairs perfectly with your top',
          '💡 Consider adding a statement necklace',
        ],
        suggestions: [
          'Try a leather jacket for an edgier look',
          'Gold accessories would complement this outfit',
          'White sneakers are on-trend this season',
        ],
      });
      setIsAnalyzing(false);
    }, 3000);
  };

  if (isAnalyzing) {
    return (
      <View style={styles.loadingContainer}>
        <LinearGradient
          colors={['#FF6B9D', '#C06C84']}
          style={styles.loadingGradient}
        >
          <ActivityIndicator size="large" color="#FFFFFF" />
          <Text style={styles.loadingText}>Analyzing your outfit...</Text>
          <Text style={styles.loadingSubtext}>
            Our AI is checking colors, style, and trends
          </Text>
        </LinearGradient>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#FF6B9D', '#C06C84']}
        style={styles.header}
      >
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Your Style Analysis</Text>
        <TouchableOpacity style={styles.shareButton}>
          <Ionicons name="share-social" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </LinearGradient>

      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Photo */}
        <Animated.View entering={FadeInUp.delay(100)} style={styles.photoContainer}>
          <Image source={{ uri: photoUri }} style={styles.photo} />
          <TouchableOpacity style={styles.saveButton}>
            <Ionicons name="heart-outline" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </Animated.View>

        {/* Overall Score */}
        <Animated.View entering={FadeInDown.delay(200)} style={styles.overallScoreCard}>
          <LinearGradient
            colors={['#667eea', '#764ba2']}
            style={styles.scoreGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <Text style={styles.overallScoreLabel}>Overall Rating</Text>
            <View style={styles.scoreCircle}>
              <Text style={styles.scoreNumber}>{analysis.overall_rating}</Text>
              <Text style={styles.scoreMax}>/10</Text>
            </View>
            <Text style={styles.scoreFeedback}>
              {analysis.overall_rating >= 9
                ? '🔥 Absolutely stunning!'
                : analysis.overall_rating >= 8
                ? '✨ Looking great!'
                : analysis.overall_rating >= 7
                ? '👍 Nice outfit!'
                : '💡 Room for improvement'}
            </Text>
          </LinearGradient>
        </Animated.View>

        {/* Score Breakdown */}
        <Animated.View entering={FadeInDown.delay(300)} style={styles.section}>
          <Text style={styles.sectionTitle}>Score Breakdown</Text>
          
          <View style={styles.scoreItem}>
            <View style={styles.scoreItemHeader}>
              <Ionicons name="shirt" size={20} color="#FF6B9D" />
              <Text style={styles.scoreItemLabel}>Style Score</Text>
            </View>
            <View style={styles.scoreBar}>
              <View
                style={[
                  styles.scoreBarFill,
                  { width: `${analysis.style_score * 10}%`, backgroundColor: '#FF6B9D' },
                ]}
              />
            </View>
            <Text style={styles.scoreItemValue}>{analysis.style_score}/10</Text>
          </View>

          <View style={styles.scoreItem}>
            <View style={styles.scoreItemHeader}>
              <Ionicons name="color-palette" size={20} color="#3498DB" />
              <Text style={styles.scoreItemLabel}>Color Harmony</Text>
            </View>
            <View style={styles.scoreBar}>
              <View
                style={[
                  styles.scoreBarFill,
                  { width: `${analysis.color_harmony * 10}%`, backgroundColor: '#3498DB' },
                ]}
              />
            </View>
            <Text style={styles.scoreItemValue}>{analysis.color_harmony}/10</Text>
          </View>

          <View style={styles.scoreItem}>
            <View style={styles.scoreItemHeader}>
              <Ionicons name="trending-up" size={20} color="#9B59B6" />
              <Text style={styles.scoreItemLabel}>Trend Match</Text>
            </View>
            <View style={styles.scoreBar}>
              <View
                style={[
                  styles.scoreBarFill,
                  { width: `${analysis.trend_match * 10}%`, backgroundColor: '#9B59B6' },
                ]}
              />
            </View>
            <Text style={styles.scoreItemValue}>{analysis.trend_match}/10</Text>
          </View>
        </Animated.View>

        {/* Detected Items */}
        <Animated.View entering={FadeInDown.delay(400)} style={styles.section}>
          <Text style={styles.sectionTitle}>Detected Items</Text>
          <View style={styles.itemsContainer}>
            {analysis.detected_items.map((item, index) => (
              <View key={index} style={styles.itemChip}>
                <Text style={styles.itemText}>{item}</Text>
              </View>
            ))}
          </View>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>
              Style: {analysis.style_category}
            </Text>
          </View>
        </Animated.View>

        {/* Color Palette */}
        <Animated.View entering={FadeInDown.delay(500)} style={styles.section}>
          <Text style={styles.sectionTitle}>Color Palette</Text>
          <View style={styles.colorsContainer}>
            {analysis.colors.map((color, index) => (
              <View
                key={index}
                style={[styles.colorCircle, { backgroundColor: color }]}
              />
            ))}
          </View>
        </Animated.View>

        {/* AI Feedback */}
        <Animated.View entering={FadeInDown.delay(600)} style={styles.section}>
          <Text style={styles.sectionTitle}>AI Feedback</Text>
          {analysis.feedback.map((item, index) => (
            <View key={index} style={styles.feedbackCard}>
              <Text style={styles.feedbackText}>{item}</Text>
            </View>
          ))}
        </Animated.View>

        {/* Suggestions */}
        <Animated.View entering={FadeInDown.delay(700)} style={styles.section}>
          <Text style={styles.sectionTitle}>Style Suggestions</Text>
          {analysis.suggestions.map((item, index) => (
            <View key={index} style={styles.suggestionCard}>
              <Ionicons name="bulb" size={20} color="#FFD700" />
              <Text style={styles.suggestionText}>{item}</Text>
            </View>
          ))}
        </Animated.View>

        {/* Action Buttons */}
        <Animated.View entering={FadeInDown.delay(800)} style={styles.actionsContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => navigation.navigate('Recommendations', { analysis })}
          >
            <LinearGradient
              colors={['#FF6B9D', '#F67280']}
              style={styles.buttonGradient}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <Ionicons name="cart" size={20} color="#FFFFFF" />
              <Text style={styles.primaryButtonText}>Shop Matching Items</Text>
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('Chat', { analysis })}
          >
            <Ionicons name="chatbubbles" size={20} color="#FF6B9D" />
            <Text style={styles.secondaryButtonText}>Ask AI Stylist</Text>
          </TouchableOpacity>
        </Animated.View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
  },
  loadingGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 20,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.8,
    marginTop: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  shareButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  photoContainer: {
    marginHorizontal: 20,
    marginTop: -40,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 5,
  },
  photo: {
    width: width - 40,
    height: (width - 40) * 1.3,
    backgroundColor: '#E0E0E0',
  },
  saveButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  overallScoreCard: {
    marginHorizontal: 20,
    marginTop: 20,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 5,
  },
  scoreGradient: {
    padding: 24,
    alignItems: 'center',
  },
  overallScoreLabel: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
    marginBottom: 12,
  },
  scoreCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  scoreNumber: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  scoreMax: {
    fontSize: 20,
    color: '#FFFFFF',
    opacity: 0.8,
  },
  scoreFeedback: {
    fontSize: 18,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  section: {
    marginHorizontal: 20,
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 16,
  },
  scoreItem: {
    marginBottom: 20,
  },
  scoreItemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  scoreItemLabel: {
    fontSize: 16,
    color: '#2C3E50',
    marginLeft: 8,
    flex: 1,
  },
  scoreItemValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    position: 'absolute',
    right: 0,
    top: 0,
  },
  scoreBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  itemsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  itemChip: {
    backgroundColor: '#FF6B9D',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
  },
  itemText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  categoryBadge: {
    backgroundColor: '#F0F0F0',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  categoryText: {
    color: '#2C3E50',
    fontSize: 14,
    fontWeight: '600',
  },
  colorsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  colorCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    borderWidth: 3,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  feedbackCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#2ECC71',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  feedbackText: {
    fontSize: 15,
    color: '#2C3E50',
    lineHeight: 22,
  },
  suggestionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFBF0',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#FFE082',
  },
  suggestionText: {
    fontSize: 15,
    color: '#2C3E50',
    marginLeft: 12,
    flex: 1,
    lineHeight: 22,
  },
  actionsContainer: {
    marginHorizontal: 20,
    marginTop: 24,
  },
  primaryButton: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
    shadowColor: '#FF6B9D',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 24,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 18,
    paddingHorizontal: 24,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#FF6B9D',
  },
  secondaryButtonText: {
    color: '#FF6B9D',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});