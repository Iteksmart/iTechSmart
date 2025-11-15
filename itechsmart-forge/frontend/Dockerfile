FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build application
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose port
EXPOSE 3032

# Serve built application
CMD ["serve", "-s", "dist", "-l", "3032"]