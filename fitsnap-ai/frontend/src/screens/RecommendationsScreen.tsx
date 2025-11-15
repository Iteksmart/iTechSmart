import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  FlatList,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');
const ITEM_WIDTH = (width - 60) / 2;

export default function RecommendationsScreen({ route, navigation }) {
  const { analysis } = route.params || {};
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = () => {
    // Mock product data
    setProducts([
      {
        id: 1,
        name: 'Casual Denim Jacket',
        brand: 'Zara',
        price: 49.99,
        image: 'https://via.placeholder.com/300x400',
        discount: 20,
        rating: 4.5,
      },
      {
        id: 2,
        name: 'White Sneakers',
        brand: 'Nike',
        price: 89.99,
        image: 'https://via.placeholder.com/300x400',
        discount: null,
        rating: 4.8,
      },
      {
        id: 3,
        name: 'Gold Necklace',
        brand: 'H&M',
        price: 19.99,
        image: 'https://via.placeholder.com/300x400',
        discount: 15,
        rating: 4.3,
      },
      {
        id: 4,
        name: 'Black Leather Bag',
        brand: 'Mango',
        price: 69.99,
        image: 'https://via.placeholder.com/300x400',
        discount: null,
        rating: 4.6,
      },
      {
        id: 5,
        name: 'Striped T-Shirt',
        brand: 'Uniqlo',
        price: 24.99,
        image: 'https://via.placeholder.com/300x400',
        discount: 10,
        rating: 4.4,
      },
      {
        id: 6,
        name: 'Blue Jeans',
        brand: 'Levi\'s',
        price: 79.99,
        image: 'https://via.placeholder.com/300x400',
        discount: null,
        rating: 4.7,
      },
    ]);
  };

  const categories = ['All', 'Tops', 'Bottoms', 'Shoes', 'Accessories'];

  const renderProduct = ({ item }) => (
    <TouchableOpacity style={styles.productCard}>
      <Image source={{ uri: item.image }} style={styles.productImage} />
      
      {item.discount && (
        <View style={styles.discountBadge}>
          <Text style={styles.discountText}>-{item.discount}%</Text>
        </View>
      )}

      <TouchableOpacity style={styles.favoriteButton}>
        <Ionicons name="heart-outline" size={20} color="#FF6B9D" />
      </TouchableOpacity>

      <View style={styles.productInfo}>
        <Text style={styles.productBrand}>{item.brand}</Text>
        <Text style={styles.productName} numberOfLines={2}>
          {item.name}
        </Text>
        
        <View style={styles.productFooter}>
          <View>
            <Text style={styles.productPrice}>${item.price}</Text>
            <View style={styles.ratingContainer}>
              <Ionicons name="star" size={12} color="#FFD700" />
              <Text style={styles.ratingText}>{item.rating}</Text>
            </View>
          </View>
          
          <TouchableOpacity style={styles.shopButton}>
            <Ionicons name="cart" size={18} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

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
        <Text style={styles.headerTitle}>Shop Your Style</Text>
        <TouchableOpacity style={styles.filterButton}>
          <Ionicons name="options" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </LinearGradient>

      {/* Match Info */}
      <View style={styles.matchInfo}>
        <Ionicons name="checkmark-circle" size={24} color="#2ECC71" />
        <Text style={styles.matchText}>
          {products.length} items matched to your style
        </Text>
      </View>

      {/* Category Filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesScroll}
        contentContainerStyle={styles.categoriesContent}
      >
        {categories.map((category) => (
          <TouchableOpacity
            key={category}
            style={[
              styles.categoryChip,
              selectedCategory === category && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(category)}
          >
            <Text
              style={[
                styles.categoryText,
                selectedCategory === category && styles.categoryTextActive,
              ]}
            >
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Products Grid */}
      <FlatList
        data={products}
        renderItem={renderProduct}
        keyExtractor={(item) => item.id.toString()}
        numColumns={2}
        contentContainerStyle={styles.productsGrid}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
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
  filterButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  matchInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    backgroundColor: '#E8F5E9',
    marginHorizontal: 20,
    marginTop: 16,
    borderRadius: 12,
  },
  matchText: {
    fontSize: 14,
    color: '#2C3E50',
    marginLeft: 8,
    fontWeight: '600',
  },
  categoriesScroll: {
    marginTop: 16,
  },
  categoriesContent: {
    paddingHorizontal: 20,
  },
  categoryChip: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  categoryChipActive: {
    backgroundColor: '#FF6B9D',
    borderColor: '#FF6B9D',
  },
  categoryText: {
    fontSize: 14,
    color: '#2C3E50',
    fontWeight: '600',
  },
  categoryTextActive: {
    color: '#FFFFFF',
  },
  productsGrid: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 20,
  },
  productCard: {
    width: ITEM_WIDTH,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    marginBottom: 16,
    marginRight: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  productImage: {
    width: '100%',
    height: ITEM_WIDTH * 1.3,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    backgroundColor: '#E0E0E0',
  },
  discountBadge: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: '#E74C3C',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  discountText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  favoriteButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  productInfo: {
    padding: 12,
  },
  productBrand: {
    fontSize: 12,
    color: '#8E8E93',
    marginBottom: 4,
  },
  productName: {
    fontSize: 14,
    color: '#2C3E50',
    fontWeight: '600',
    marginBottom: 8,
    height: 36,
  },
  productFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  productPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  ratingText: {
    fontSize: 12,
    color: '#8E8E93',
    marginLeft: 4,
  },
  shopButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#FF6B9D',
    justifyContent: 'center',
    alignItems: 'center',
  },
});