# QuarryDepthFinder 🏔️

A comprehensive geospatial analysis application for calculating quarry/excavation depths, volumes, and terrain analysis using Digital Elevation Models (DEMs). Built with Flask and advanced terrain analytics.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Docker Support](#docker-support)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**QuarryDepthFinder** is a Python-based web application designed to analyze quarry and excavation sites using Digital Elevation Model (DEM) data. The application processes raster DEM files to calculate:

- **Quarry depth** mapping
- **Volume estimation** with multiple calculation methods
- **Terrain analysis** including slope and aspect
- **3D visualization** of excavation sites
- **Automatic report generation**

The application provides both a web interface and REST API endpoints for integration with other systems.

---

## Features

### Core Analysis
✅ **Depth Calculation**
- Automatic surface elevation estimation using gradient descent optimization
- Manual reference point selection for precise measurements
- Multiple depth estimation methods
- Pixel-level accuracy

✅ **Volume Computation**
- Pixel-based volume calculation
- Integration-based volume estimation
- Material categorization (shallow, medium, deep, very deep)
- Multiple calculation methodologies for validation

✅ **Terrain Analysis**
- Slope analysis
- Aspect calculation
- Hillshade visualization
- 3D terrain context

✅ **Visualization**
- Discrete depth maps with contour lines
- Professional-grade matplotlib visualizations
- Interactive 3D visualization (Three.js)
- Histogram distribution analysis
- Elevation data rendering

✅ **Reporting**
- Automated PDF report generation
- Comprehensive statistics summary
- Visual analytics

✅ **Advanced Features**
- Manual reference points for custom elevation data
- Edge-based terrain sampling
- Outlier filtering using statistical methods
- NoData handling
- CRS-aware coordinate transformations

---

## Installation

### Prerequisites
- Python 3.8+
- MongoDB (for data persistence)
- pip

### Step 1: Clone the Repository
```bash
git clone https://github.com/Vishweswarann/QuarryDepthFinder.git
cd QuarryDepthFinder
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MongoDB
Set your MongoDB connection URI in an environment variable:
```bash
export MONGO_URI="mongodb://localhost:27017/QuarryDepthFinder"
```

### Step 5: Run the Application
```bash
python run.py
```

The application will start at `http://localhost:5000`

---

## Usage

### Web Interface
1. Navigate to `http://localhost:5000`
2. Upload your DEM file (GeoTIFF format recommended)
3. Optionally set a reference point (latitude/longitude)
4. Click "Analyze" to process
5. View results and download visualizations/reports

### REST API

#### Basic Analysis
```bash
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: DEM file (GeoTIFF)
- reference_lat (optional): Reference latitude
- reference_lng (optional): Reference longitude
```

#### Advanced Analysis
```bash
POST /advanced/analyze
Content-Type: multipart/form-data

Parameters:
- file: DEM file
- method: "gradient_descent" or "edge_estimation"
- learning_rate (optional): 0.01-1.0
- iterations (optional): 100-10000
```

#### Generate Report
```bash
POST /advanced/generate-report
Content-Type: application/json

{
  "depth_map": [...],
  "stats": {...},
  "output_format": "pdf"
}
```

---

## Project Structure

```
QuarryDepthFinder/
├── main.py                    # Flask app factory
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
│
├── routes.py                  # Main API routes
├── advanced_routes.py         # Advanced feature routes
├── test_depth.py              # Test endpoints
│
├── depth_analysis.py          # Core depth calculation engine
│   ├── gradient_descent_surface_optimization()
│   ├── calculate_quarry_depth()
│   ├── estimate_original_surface()
│   └── generate_depth_visualization()
│
├── volume_calculator.py       # Volume estimation module
│   ├── calculate_excavation_volume()
│   ├── calculate_integral_volume()
│   └── categorize_excavation_material()
│
├── slope_analysis.py          # Terrain slope analysis
├── three_visualization.py     # 3D visualization (Three.js)
├── report_generator.py        # PDF report generation
├── raster.py                  # Raster utilities
├── extraFunctions.py          # Helper functions
│
├── static/                    # Frontend assets (CSS, JS)
├── templates/                 # HTML templates
│
├── 3d/                        # 3D visualization files
├── cropped.tif               # Sample DEM file
└── dem_tile.tif              # Sample DEM file
```

---

## API Documentation

### Endpoints

#### 1. **POST /analyze**
Main quarry analysis endpoint
- **Input**: DEM file, optional reference point
- **Output**: Depth map, volume statistics, visualization
- **Status**: 200 (Success), 400 (Bad Request), 500 (Error)

#### 2. **POST /advanced/analyze**
Advanced analysis with custom parameters
- **Methods**: `gradient_descent`, `edge_estimation`
- **Parameters**: learning_rate, iterations
- **Output**: Detailed analysis results

#### 3. **GET /visualization/<file_id>**
Retrieve generated visualizations
- **Output**: PNG image

#### 4. **POST /advanced/generate-report**
Generate comprehensive PDF report
- **Input**: Analysis results
- **Output**: PDF file

#### 5. **GET /test/sample-data**
Get sample analysis data for testing

---

## Configuration

### Environment Variables
```bash
# MongoDB connection
MONGO_URI=mongodb://localhost:27017/QuarryDepthFinder

# Flask settings
FLASK_ENV=development  # or production
FLASK_DEBUG=True       # or False

# Application settings
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=104857600  # 100MB
```

### Flask Configuration (main.py)
```python
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/QuarryDepthFinder")
app.secret_key = "vanakam"
```

---

## Docker Support

### Build Docker Image
```bash
docker build -t quarry-depth-finder .
```

### Run Container
```bash
docker run -p 5000:5000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/QuarryDepthFinder" \
  quarry-depth-finder
```

### Docker Compose (Optional)
```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      MONGO_URI: "mongodb://mongo:27017/QuarryDepthFinder"
    depends_on:
      - mongo
  
  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
```

---

## Key Algorithms

### Gradient Descent Surface Optimization
- Uses edge pixels as training data
- Minimizes mean squared error
- Iterative parameter updates with convergence detection
- Tolerance: 0.0001m elevation change

**Example Output:**
```
📊 Edge data: 1850 points, range: 245.3m to 265.7m
🔍 Starting gradient descent from: 263.45m
   Iteration 0: surface=263.45m, gradient=0.156234
   Iteration 100: surface=255.12m, gradient=0.002345
✅ Converged after 234 iterations
🎯 Gradient Descent Surface: 255.08m
```

### Volume Calculation Methods
1. **Pixel Method**: Sum of (depth × pixel_area)
2. **Integration Method**: Numerical Simpson's integration
3. **Material Categorization**: Depth-based binning

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.2 | Web framework |
| Flask-PyMongo | 2.3.0 | MongoDB integration |
| numpy | ≥2.1.0 | Numerical computing |
| scipy | ≥1.14.0 | Scientific computing |
| rasterio | ≥1.4.0 | GeoTIFF processing |
| matplotlib | ≥3.9.0 | Visualization |
| pyproj | ≥3.6.1 | Coordinate transformations |
| fpdf | 1.7.2 | PDF generation |
| gunicorn | 21.2.0 | Production server |

---

## Sample Data

The repository includes sample DEM files for testing:
- `dem_tile.tif` - Full DEM dataset
- `cropped.tif` - Cropped quarry area

Run tests with sample data:
```bash
python test_depth.py
```

---

## Performance Considerations

- **DEM File Size**: Recommended <50MB for optimal performance
- **Pixel Resolution**: Best results with 5-50m pixel size
- **Processing Time**: 
  - Gradient descent: 30-60 seconds
  - Volume calculation: 5-15 seconds
  - Report generation: 10-20 seconds
- **Memory Usage**: ~3-5x file size during processing

---

## Troubleshooting

### Issue: "DEM file not found"
**Solution**: Ensure file path is correct and file is in supported format (GeoTIFF)

### Issue: "Gradient descent failed to converge"
**Solution**: Try adjusting learning_rate (default: 0.1) or iterations (default: 1000)

### Issue: MongoDB connection error
**Solution**: Verify MongoDB is running and MONGO_URI is correctly set
```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017/QuarryDepthFinder"
```

### Issue: NaN values in output
**Solution**: Ensure DEM file has valid data and NoData values are properly configured

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Development

### Running Tests
```bash
python -m pytest test_depth.py -v
```

### Code Structure Guidelines
- Use type hints for function parameters
- Include docstrings for all functions
- Follow PEP 8 style guide
- Add error handling with try-except blocks

---

## License

This project is currently open source. See LICENSE file for details (if applicable).

---

## Authors

**Vishweswarann** - [GitHub Profile](https://github.com/Vishweswarann)

---

## Acknowledgments

- Geospatial analysis techniques inspired by USGS DEM analysis methods
- Visualization methods based on matplotlib best practices
- 3D visualization powered by Three.js

---

## Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review test cases in `test_depth.py`

---

## Roadmap 🚀

- [ ] Web UI improvements
- [ ] Real-time analysis progress tracking
- [ ] Batch processing for multiple files
- [ ] Additional terrain metrics (curvature, rugosity)
- [ ] Export to GeoJSON/Shapefile formats
- [ ] Interactive mapping interface (Leaflet/Mapbox)
- [ ] Machine learning-based surface estimation
- [ ] Cloud deployment templates (AWS/GCP/Azure)

---

**Last Updated**: May 2026  
**Status**: Active Development
