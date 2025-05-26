# Job Recommender System

A comprehensive AI-powered job recommendation system with FastAPI backend, Next.js frontend, and Streamlit interface. Features advanced vector embeddings, multi-language support with real-time translation, and intelligent matching algorithms.

## 🌟 Features

### Core Functionality
- **AI-Powered Recommendations**: Job and candidate matching using vector embeddings with Ollama
- **Skill Gap Analysis**: Intelligent analysis of candidate skills vs. job requirements
- **Career Path Recommendations**: AI-driven career progression suggestions
- **Project Recommendations**: Matching candidates with relevant projects
- **Market Trends Analysis**: Real-time job market insights and trends

### Multi-Language Support
- **English and Arabic Support**: Complete RTL (Right-to-Left) layout for Arabic
- **Real-time Translation**: Powered by LibreTranslate for instant page translation
- **Image OCR Translation**: Extract and translate text from images using Tesseract.js
- **Translation Memory**: Local caching system for improved performance
- **Language-aware Components**: Smart UI components that adapt to language direction

### User Management
- **Dual User Types**: Separate interfaces for employers and candidates
- **Profile Management**: Comprehensive profile creation and management
- **Application Tracking**: Complete job application lifecycle management
- **Recommendation Feedback**: Machine learning from user interactions

## 🏗️ Project Structure

```
Latest_lamma/
├── backend/                     # FastAPI backend
│   ├── app.py                  # Main FastAPI application
│   ├── utils/                  # Core utilities
│   │   ├── models.py           # Pydantic models
│   │   ├── database.py         # MongoDB operations
│   │   ├── embedding.py        # Vector embedding functions
│   │   └── extended_models.py  # Extended data models
│   ├── routers/                # API route modules
│   ├── tests/                  # Backend-specific tests
│   └── init_db.py             # Database initialization
├── frontend/                   # Next.js frontend
│   └── lnd-nexus/             # Next.js application
│       ├── app/               # Next.js app directory
│       │   ├── components/    # React components
│       │   │   ├── LanguageSwitcher.tsx    # Language switching UI
│       │   │   ├── TranslatableImage.tsx   # Image translation component
│       │   │   └── TranslatableContent.tsx # Content translation component
│       │   ├── lib/           # Translation utilities
│       │   │   ├── translate.ts           # Core translation functions
│       │   │   ├── imageTranslate.ts      # Image OCR and translation
│       │   │   └── translationMemory.ts   # Translation caching system
│       │   ├── locales/       # Translation files
│       │   │   ├── en.json    # English translations
│       │   │   └── ar.json    # Arabic translations
│       │   └── providers/     # React context providers
│       └── .env.local         # Frontend environment variables
├── pages/                      # Streamlit pages
│   ├── candidate_profile.py   # Candidate management
│   ├── employer_profile.py    # Employer management
│   ├── job_recommendations.py # Job matching
│   └── skill_gap.py          # Skill analysis
├── tests/                      # Organized test directory
│   ├── test_suite/            # Main test suite
│   ├── workflow_functions/    # Test workflow utilities
│   └── PROJECT_CLEANUP_REPORT.txt # Cleanup documentation
├── test/                       # Additional test organization
│   ├── translation_modules/   # Translation testing utilities
│   ├── mongodb_tests/         # Database testing
│   ├── temporary_files/       # Temporary test files
│   └── documentation/         # Test documentation
├── memory-bank/               # Project documentation and context
├── utils/                     # Shared utilities
├── myenv/                     # Python virtual environment
├── setup.py                   # Automated setup script
├── run_app.py                 # Application runner
├── run_nextjs_app.py          # Next.js application runner
└── README.md                  # This file
```

## 🔧 Prerequisites

### Required Software
- **Python 3.10**: Specifically required for optimal compatibility
- **Node.js 18+**: For Next.js frontend
- **MongoDB**: Database for storing application data
- **Docker**: For LibreTranslate service (optional but recommended)

### AI Services
- **Ollama**: For local AI embeddings and language models
- **LibreTranslate**: For real-time translation (runs in Docker)

### Installation Links
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [Node.js](https://nodejs.org/)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Ollama](https://ollama.com/)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

The setup script will automatically install all dependencies and configure the application:

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Direct Python:**
```bash
python setup.py
```

### What the Setup Script Does:
1. ✅ Installs Ollama and required AI models
2. ✅ Sets up LibreTranslate Docker container
3. ✅ Creates Python 3.10 virtual environment
4. ✅ Installs all Python dependencies
5. ✅ Installs Next.js frontend dependencies
6. ✅ Configures environment variables
7. ✅ Initializes MongoDB database
8. ✅ Creates platform-specific run scripts
9. ✅ Sets up translation modules
10. ✅ Offers to run the application immediately

### Option 2: Manual Installation

If you prefer manual setup:

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Latest_lamma
```

2. **Create Python 3.10 virtual environment:**
```bash
python3.10 -m venv myenv
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
pip install streamlit
```

4. **Install frontend dependencies:**
```bash
cd frontend/lnd-nexus
npm install
npm install tesseract.js lucide-react @radix-ui/react-dropdown-menu
cd ../..
```

5. **Set up environment variables:**
```bash
# Create .env file with your configuration
echo "MONGODB_URL=mongodb://localhost:27017" > .env
echo "OLLAMA_API_BASE=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=llama3.2" >> .env
echo "LIBRETRANSLATE_URL=http://localhost:5000" >> .env
```

6. **Initialize database:**
```bash
python backend/init_db.py
```

## 🏃‍♂️ Running the Application

### Complete Application (Backend + Frontend)

**Streamlit Interface:**
```bash
python run_app.py
```
- Backend API: http://localhost:8000
- Streamlit UI: http://localhost:8501

**Next.js Interface:**
```bash
python run_nextjs_app.py
```
- Backend API: http://localhost:8000
- Next.js UI: http://localhost:3000

### Individual Services

**Backend Only:**
```bash
python run_backend.py
```
- API Documentation: http://localhost:8000/docs

**Next.js Frontend Only:**
```bash
cd frontend/lnd-nexus
npm run dev
```
- Development server: http://localhost:3000

**Streamlit Frontend Only:**
```bash
streamlit run streamlit_app.py
```
- Streamlit app: http://localhost:8501

## 🌐 Translation Features

### Supported Languages
- **English**: Primary language with full feature support
- **Arabic**: Complete RTL layout with real-time translation

### Translation Capabilities
- **Page Translation**: Translate entire pages instantly
- **Image OCR**: Extract and translate text from images
- **Translation Memory**: Cache translations for improved performance
- **Language Detection**: Automatic source language detection
- **RTL Support**: Proper right-to-left layout for Arabic

### Translation Services Setup

**LibreTranslate (Docker):**
```bash
docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate:latest
```

**Verify Translation Service:**
```bash
python test/mongodb_tests/test_mongodb_setup.py
```

## 🧪 Testing

### Comprehensive Test Suite

**Run All Tests:**
```bash
python tests/run_full_tests.py
```

**Visual Demo:**
```bash
python tests/visual_demo.py
```

**Test with Detailed Logging:**
```bash
python tests/run_full_tests.py --show-requests
```

### Test Organization

The project uses a well-organized test structure:

- `tests/` - Main test suite with comprehensive API and workflow tests
- `test/translation_modules/` - Translation functionality tests
- `test/mongodb_tests/` - Database connectivity tests
- `test/temporary_files/` - Temporary and experimental test files
- `backend/tests/` - Backend-specific unit tests

### Test Features
- **Automated Service Management**: Starts/stops services automatically
- **Complete User Flows**: Tests registration, login, job creation, applications
- **API Endpoint Testing**: Comprehensive API validation
- **Visual Browser Testing**: Automated UI testing with Selenium
- **Error Reporting**: Detailed error diagnostics and reporting

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=job_recommender
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2
SECRET_KEY=your_secret_key_here
LIBRETRANSLATE_URL=http://localhost:5000
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_LIBRETRANSLATE_URL=http://localhost:5000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Service Ports
- **Backend API**: 8000
- **Streamlit**: 8501
- **Next.js**: 3000
- **MongoDB**: 27017
- **Ollama**: 11434
- **LibreTranslate**: 5000

## 🛠️ Development

### Adding New Features

1. **Backend**: Add routes in `backend/routers/`
2. **Frontend**: Add components in `frontend/lnd-nexus/app/components/`
3. **Streamlit**: Add pages in `pages/`
4. **Tests**: Add tests in appropriate `test/` subdirectories

### Translation Development

1. **Add Translation Functions**: Extend `frontend/lnd-nexus/app/lib/translate.ts`
2. **Update Language Files**: Modify `frontend/lnd-nexus/app/locales/`
3. **Test Translation**: Use `test/translation_modules/verify_translation_modules.py`

### Database Development

1. **Models**: Update `backend/utils/models.py`
2. **Database Operations**: Extend `backend/utils/database.py`
3. **Test Database**: Use `test/mongodb_tests/test_mongodb_setup.py`

## 🐛 Troubleshooting

### Common Issues

**Python Version Issues:**
```bash
# Verify Python 3.10 is installed
python3.10 --version
# or
py -3.10 --version
```

**MongoDB Connection:**
```bash
# Test MongoDB connection
python test/mongodb_tests/test_mongodb_setup.py
```

**Translation Modules Missing:**
```bash
# Fix translation modules
python test/translation_modules/fix_translation_modules.py
```

**Ollama Not Running:**
```bash
# Start Ollama service
ollama serve
# Pull required model
ollama pull llama3.2
```

**LibreTranslate Not Available:**
```bash
# Start LibreTranslate container
docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate:latest
```

### Service Management

**Stop All Services:**
```bash
python stop_app.py
```

**Check Service Status:**
```bash
# Check if services are running
curl http://localhost:8000/docs  # Backend
curl http://localhost:3000       # Next.js
curl http://localhost:8501       # Streamlit
curl http://localhost:5000/languages  # LibreTranslate
```

## 📚 Documentation

### Additional Documentation
- [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md) - Detailed running instructions
- [LANGUAGE_SUPPORT.md](LANGUAGE_SUPPORT.md) - Language feature documentation
- [NEXTJS_INTEGRATION.md](NEXTJS_INTEGRATION.md) - Next.js frontend details
- [TRANSLATION_FEATURE.md](TRANSLATION_FEATURE.md) - Translation system details
- [test/PROJECT_CLEANUP_REPORT.txt](test/PROJECT_CLEANUP_REPORT.txt) - Project organization

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

### Development Guidelines
- Use Python 3.10 for all development
- Add tests to appropriate `test/` subdirectories
- Update translation files for new UI text
- Follow existing code organization patterns
- Document new features in README.md

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section above
2. Review the documentation in the `memory-bank/` directory
3. Run the diagnostic scripts in `test/` directories
4. Check the project cleanup report for file organization

## 🔄 Version History

- **Latest**: Multi-language support with real-time translation
- **Previous**: AI-powered recommendations with vector embeddings
- **Initial**: Basic job recommendation system

---

**Note**: This project requires Python 3.10 specifically for optimal compatibility with all dependencies and features. The automated setup script will detect and use Python 3.10 automatically. 