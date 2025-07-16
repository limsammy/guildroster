# GuildRoster Frontend

A React-based frontend for the GuildRoster application with WoW-themed design and comprehensive authentication.

## Features

- **WoW-themed UI** - Dark theme with amber/orange accents
- **Authentication System** - Complete login/logout functionality
- **Responsive Design** - Works on desktop, tablet, and mobile
- **TypeScript** - Full type safety
- **Testing** - Unit tests with Vitest and E2E tests with Cypress

## Quick Start

### Prerequisites

- Node.js 18+ 
- FastAPI backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Run E2E tests
npm run test:e2e
```

## Authentication Setup

The frontend connects to the FastAPI backend for authentication. Make sure your backend is running and has:

1. **User accounts created** - Use the backend script to create users
2. **CORS configured** - Backend should allow requests from `http://localhost:5173`
3. **Login endpoint** - Available at `POST /users/login`

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Authentication (optional - for development/testing)
VITE_AUTH_TOKEN=your_bearer_token_here

# Environment
NODE_ENV=development
```

### Testing Authentication

#### Option 1: Using Environment Token (Recommended for Development)

1. **Add your bearer token to `.env`**:
   ```env
   VITE_AUTH_TOKEN=your_bearer_token_here
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. **You'll be automatically authenticated** - The app will use your environment token

#### Option 2: Using Login Form

1. **Start the backend**:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```

2. **Create a test user**:
   ```bash
   python scripts/create_superuser.py
   ```

3. **Start the frontend**:
   ```bash
   npm run dev
   ```

4. **Test login** - Navigate to `/login` and use your credentials

## Project Structure

```
app/
├── api/           # API services and types
├── components/    # Reusable UI components
│   ├── ui/       # Base UI components (Button, Card, etc.)
│   ├── layout/   # Layout components (Navigation, Footer)
│   └── sections/ # Page sections (Hero)
├── contexts/     # React contexts (AuthContext)
└── routes/       # Page components
```

## API Integration

The frontend uses a centralized API service layer:

- **AuthService** - Handles login, logout, and token management
- **Axios interceptors** - Automatically add auth tokens to requests
- **Error handling** - Graceful error handling for API failures
- **Token storage** - Secure localStorage management

## Testing

### Unit Tests
```bash
npm test                    # Run all tests
npm run test:watch         # Watch mode
npm run test:coverage      # Coverage report
```

### E2E Tests
```bash
npm run cypress:open       # Open Cypress UI
npm run test:e2e          # Run headless tests
```

## Development

### Adding New Routes

1. Create the route component in `app/routes/`
2. Add the route to `app/routes.ts`
3. Run `npm run typecheck` to generate types

### Styling

The app uses Tailwind CSS with custom WoW-themed colors:
- Primary: Amber/Orange gradients
- Background: Slate grays
- Accents: Red for danger, blue for info

### State Management

- **AuthContext** - Manages authentication state
- **Local Storage** - Persists tokens and user info
- **React Router** - Handles navigation and routing

## Deployment

### Build for Production
```bash
npm run build
```

### Docker
```bash
docker build -t guildroster-frontend .
docker run -p 3000:3000 guildroster-frontend
```

## Troubleshooting

### Common Issues

1. **CORS Errors** - Ensure backend allows frontend origin
2. **API Connection** - Check `VITE_API_URL` environment variable
3. **Type Errors** - Run `npm run typecheck` to regenerate types
4. **Test Failures** - Ensure backend is running for integration tests

### Debug Mode

Enable debug logging by setting `NODE_ENV=development` in your environment.
