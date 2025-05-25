# Frontend Status

## Dual Frontend Approach

The job recommendation system implements a dual frontend approach:

### 1. Streamlit App (Testing/Debug Frontend)
- Located in `streamlit_app.py` and the `pages/` directory
- Primarily used for testing, debugging, and API validation
- Simple interface for interacting with all backend features
- Dashboards for both candidate and employer user types
- Pages for profile management, job recommendations, skill gap analysis, and other features
- Quick prototype and API testing environment

### 2. Next.js App (Main Production Frontend)
- Located in `frontend/lnd-nexus/` directory
- Built with modern React/Next.js (version 15.3.2)
- Uses TypeScript for type safety
- Employs Tailwind CSS for styling
- Component-based architecture following modern frontend practices
- Organized around app router pattern with dedicated sections:
  - Authentication (login/register)
  - Dashboard
  - Jobs
  - Professionals
  - Resources
  - Forum
  - Services

## Integration Architecture
- Both frontends communicate with the same FastAPI backend
- Next.js frontend runs on port 3005 to avoid conflicts
- FastAPI backend runs on port 8000
- CORS middleware configured to allow cross-origin requests
- Special run scripts (`run_nextjs_app.py`, `run_nextjs_prod.py`) manage concurrent execution of backend and Next.js frontend

## Current Development Status
- Next.js frontend is actively being developed as the main production frontend
- Streamlit frontend continues to serve as a testing/debugging tool
- Both share the same backend API endpoints
- Authentication flows, profile management, and core features implemented in both frontends
- Next.js implementation includes enhanced UI components:
  - Hero sections
  - How It Works explainers
  - Testimonials
  - Featured listings
  - Resource hub
  - Pricing information
  - Call-to-action components

## Deployment Options
- **Development Mode**:
  - `run_nextjs_app.bat`/`run_nextjs_app.sh`
  - Hot-reloading for both frontend and backend
  - Suitable for active development

- **Production Mode**:
  - `run_nextjs_prod.bat`/`run_nextjs_prod.sh`
  - Optimized build with server-side rendering
  - Configured for deployment environments

- **Separate Components**:
  - Backend and frontend can be run independently
  - Useful for focused development on specific components

## Key Features Available in Both Frontends
- User authentication (registration/login)
- Profile management (candidates/employers)
- Job recommendations
- Skill gap analysis
- Talent search
- Career path recommendations
- Learning recommendations
- Recommendation feedback system
- Skill clusters analysis
- Market trend predictions

## Frontend Component Structure (Next.js)
- Layout components for consistent UI
- Authentication flows
- Dashboard views for different user types
- Interactive job and candidate listings
- Visualization components for analytics
- Form components for data entry
- Navigation components

## Frontend Component Structure (Streamlit)
- Multi-page application with sidebar navigation
- Interactive data visualizations
- Form inputs for API testing
- JSON response displays
- Authentication state management
- Profile management interfaces
- Recommendation displays

## Development Approach
The project follows a progressive enhancement approach:
- Streamlit app was the initial frontend for rapid testing and API validation
- Next.js frontend is being developed as a more polished, production-ready interface
- Both frontends will continue to be maintained during development
- Long-term focus is on the Next.js frontend for production use

## Technical Considerations
- Cross-browser compatibility
- Responsive design for various device sizes
- Accessibility considerations
- Performance optimization
- Authentication token management
- Error handling and user feedback 