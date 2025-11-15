import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const [stats, setStats] = useState({
    totalScans: 24,
    avgScore: 8.7,
    savedLooks: 12,
  });

  const [recentScans, setRecentScans] = useState([
    {
      id: 1,
      image: 'https://via.placeholder.com/300x400',
      score: 9.2,
      date: '2 hours ago',
    },
    {
      id: 2,
      image: 'https://via.placeholder.com/300x400',
      score: 8.5,
      date: 'Yesterday',
    },
    {
      id: 3,
      image: 'https://via.placeholder.com/300x400',
      score: 8.9,
      date: '3 days ago',
    },
  ]);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <LinearGradient
        colors={['#FF6B9D', '#C06C84']}
        style={styles.header}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>Hello, Sarah! 👋</Text>
            <Text style={styles.subtitle}>Ready to look amazing today?</Text>
          </View>
          <TouchableOpacity style={styles.notificationButton}>
            <Ionicons name="notifications-outline" size={24} color="#FFFFFF" />
            <View style={styles.badge} />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Ionicons name="camera" size={24} color="#FF6B9D" />
          <Text style={styles.statNumber}>{stats.totalScans}</Text>
          <Text style={styles.statLabel}>Total Scans</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="star" size={24} color="#FFD700" />
          <Text style={styles.statNumber}>{stats.avgScore}</Text>
          <Text style={styles.statLabel}>Avg Score</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="heart" size={24} color="#FF6B9D" />
          <Text style={styles.statNumber}>{stats.savedLooks}</Text>
          <Text style={styles.statLabel}>Saved Looks</Text>
        </View>
      </View>

      {/* Main CTA */}
      <TouchableOpacity
        style={styles.mainCTA}
        onPress={() => navigation.navigate('Camera')}
        activeOpacity={0.9}
      >
        <LinearGradient
          colors={['#FF6B9D', '#F67280']}
          style={styles.ctaGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.ctaContent}>
            <View style={styles.ctaIcon}>
              <Ionicons name="camera" size={32} color="#FFFFFF" />
            </View>
            <View style={styles.ctaText}>
              <Text style={styles.ctaTitle}>Scan Your Outfit</Text>
              <Text style={styles.ctaSubtitle}>Get instant AI feedback</Text>
            </View>
            <Ionicons name="arrow-forward" size={24} color="#FFFFFF" />
          </View>
        </LinearGradient>
      </TouchableOpacity>

      {/* Recent Scans */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Scans</Text>
          <TouchableOpacity onPress={() => navigation.navigate('MyLooks')}>
            <Text style={styles.seeAll}>See All</Text>
          </TouchableOpacity>
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.scansScroll}
        >
          {recentScans.map((scan) => (
            <TouchableOpacity
              key={scan.id}
              style={styles.scanCard}
              onPress={() => navigation.navigate('Analysis', { scanId: scan.id })}
            >
              <Image source={{ uri: scan.image }} style={styles.scanImage} />
              <View style={styles.scanOverlay}>
                <View style={styles.scoreBadge}>
                  <Ionicons name="star" size={16} color="#FFD700" />
                  <Text style={styles.scoreText}>{scan.score}</Text>
                </View>
              </View>
              <Text style={styles.scanDate}>{scan.date}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => navigation.navigate('Chat')}
          >
            <View style={[styles.actionIcon, { backgroundColor: '#E8F5E9' }]}>
              <Ionicons name="chatbubbles" size={24} color="#4CAF50" />
            </View>
            <Text style={styles.actionLabel}>AI Stylist</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => navigation.navigate('Recommendations')}
          >
            <View style={[styles.actionIcon, { backgroundColor: '#FFF3E0' }]}>
              <Ionicons name="shirt" size={24} color="#FF9800" />
            </View>
            <Text style={styles.actionLabel}>Shop Looks</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => navigation.navigate('MyLooks')}
          >
            <View style={[styles.actionIcon, { backgroundColor: '#FCE4EC' }]}>
              <Ionicons name="heart" size={24} color="#E91E63" />
            </View>
            <Text style={styles.actionLabel}>Favorites</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => navigation.navigate('Profile')}
          >
            <View style={[styles.actionIcon, { backgroundColor: '#E3F2FD' }]}>
              <Ionicons name="settings" size={24} color="#2196F3" />
            </View>
            <Text style={styles.actionLabel}>Settings</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Pro Upgrade Banner */}
      <TouchableOpacity style={styles.upgradeBanner} activeOpacity={0.9}>
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.upgradeBannerGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.upgradeContent}>
            <Ionicons name="star" size={32} color="#FFD700" />
            <View style={styles.upgradeText}>
              <Text style={styles.upgradeTitle}>Upgrade to Pro</Text>
              <Text style={styles.upgradeSubtitle}>
                Unlock AI Chat, exclusive deals & more
              </Text>
            </View>
            <View style={styles.upgradePrice}>
              <Text style={styles.priceText}>$3</Text>
              <Text style={styles.priceLabel}>/mo</Text>
            </View>
          </View>
        </LinearGradient>
      </TouchableOpacity>

      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#FFD700',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginTop: -20,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
  },
  mainCTA: {
    marginHorizontal: 20,
    marginBottom: 24,
    borderRadius: 20,
    overflow: 'hidden',
    shadowColor: '#FF6B9D',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 5,
  },
  ctaGradient: {
    padding: 20,
  },
  ctaContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ctaIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  ctaText: {
    flex: 1,
  },
  ctaTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  ctaSubtitle: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  seeAll: {
    fontSize: 14,
    color: '#FF6B9D',
    fontWeight: '600',
  },
  scansScroll: {
    paddingLeft: 20,
    paddingRight: 10,
  },
  scanCard: {
    width: 140,
    marginRight: 12,
  },
  scanImage: {
    width: 140,
    height: 200,
    borderRadius: 16,
    backgroundColor: '#E0E0E0',
  },
  scanOverlay: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  scoreBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  scanDate: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 8,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
  },
  actionCard: {
    width: (width - 60) / 4,
    alignItems: 'center',
    marginBottom: 16,
  },
  actionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 12,
    color: '#2C3E50',
    textAlign: 'center',
  },
  upgradeBanner: {
    marginHorizontal: 20,
    borderRadius: 20,
    overflow: 'hidden',
    marginBottom: 20,
  },
  upgradeBannerGradient: {
    padding: 20,
  },
  upgradeContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  upgradeText: {
    flex: 1,
    marginLeft: 16,
  },
  upgradeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  upgradeSubtitle: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  upgradePrice: {
    alignItems: 'center',
  },
  priceText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  priceLabel: {
    fontSize: 12,
    color: '#FFFFFF',
    opacity: 0.8,
  },
});