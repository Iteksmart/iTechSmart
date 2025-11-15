# iTechSmart Sandbox - Frontend

Modern React + TypeScript frontend for the iTechSmart Sandbox platform.

## Features

- **Dashboard**: Overview of all sandboxes with real-time status
- **Sandbox Management**: Create, start, stop, and terminate sandboxes
- **Code Editor**: Monaco-based editor with syntax highlighting
- **Resource Monitoring**: Real-time charts for CPU, memory, GPU, disk, and network
- **File Management**: Upload, download, and manage sandbox files
- **Test Execution**: Run and monitor tests across all iTechSmart products

## Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Monaco Editor**: VS Code-powered code editor
- **Recharts**: Beautiful, composable charts
- **Axios**: HTTP client for API calls
- **Lucide React**: Modern icon library

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:3033`

### Environment Variables

Create a `.env` file with the following variables:

```env
VITE_API_URL=http://localhost:8033
VITE_ENV=development
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── SandboxCard.tsx
│   │   └── MetricsChart.tsx
│   ├── pages/          # Page components
│   │   ├── Dashboard.tsx
│   │   ├── SandboxList.tsx
│   │   ├── CreateSandbox.tsx
│   │   ├── SandboxDetail.tsx
│   │   └── CodeEditor.tsx
│   ├── services/       # API services
│   │   └── api.ts
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   ├── utils/          # Utility functions
│   │   └── helpers.ts
│   ├── styles/         # Global styles
│   │   └── globals.css
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── index.html          # HTML template
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
├── vite.config.ts      # Vite config
└── README.md           # This file
```

## Building for Production

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

The built files will be in the `dist` directory.

## Docker

### Build Docker Image

```bash
docker build -t itechsmart-sandbox-frontend .
```

### Run Docker Container

```bash
docker run -p 3033:3033 itechsmart-sandbox-frontend
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8033`. All API calls are handled through the `services/api.ts` module.

### API Endpoints

- **Sandboxes**: `/api/sandboxes`
- **Files**: `/api/sandboxes/{id}/files`
- **Snapshots**: `/api/snapshots`
- **Tests**: `/api/tests`
- **Templates**: `/api/templates`

## Features in Detail

### Dashboard

- Overview of all sandboxes
- Quick stats (total, running, stopped, creating)
- Recent sandboxes with quick actions
- Create new sandbox button

### Sandbox Management

- List all sandboxes with filtering and search
- Create new sandboxes with custom configuration
- View detailed sandbox information
- Start, stop, and terminate sandboxes
- Real-time status updates

### Code Editor

- Monaco editor with syntax highlighting
- Support for multiple languages (Python, JavaScript, TypeScript, Java, C++, Go, Rust)
- Run code directly in sandbox
- Upload and download code files
- Real-time output display

### Resource Monitoring

- Real-time CPU usage charts
- Memory usage visualization
- GPU utilization (if available)
- Disk I/O metrics
- Network traffic graphs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Copyright © 2025 iTechSmart Inc.. All rights reserved.

## Support

For support, please contact the iTechSmart Inc. or visit our documentation.