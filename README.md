# QuarryDepthFinder

A sophisticated geospatial analysis platform that uses Digital Elevation Models (DEM) to calculate quarry depth, volume, slope analysis, and generate comprehensive reports with 3D visualizations.

## Overview

QuarryDepthFinder is a Python-based web application built with Flask that analyzes mining and quarry sites using raster DEM data. It provides advanced geospatial analysis capabilities including depth calculation, volume estimation, slope analysis, and generates detailed PDF reports with 3D terrain visualizations.

## Features

- **Depth Analysis**: Calculate quarry/pit depth using DEM data
- **Volume Calculation**: Estimate excavation volumes based on depth and area
- **Slope Analysis**: Analyze terrain slopes and stability zones
- **3D Visualization**: Generate interactive 3D models of terrain using Three.js
- **PDF Report Generation**: Comprehensive reports with maps, charts, and statistics
- **MongoDB Integration**: Persistent storage of analysis results
- **RESTful API**: Full REST API for programmatic access
- **Docker Support**: Containerized deployment ready
- **Advanced Analytics**: Multiple advanced analysis features and algorithms

## Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-PyMongo** - MongoDB integration
- **NumPy & SciPy** - Scientific computing
- **Rasterio** - Raster data processing
- **PyProj** - Coordinate system handling

### Frontend & Visualization
- **Three.js** - 3D visualization
- **Matplotlib** - Charts and plots
- **FPDF** - PDF report generation

### DevOps
- **Docker** - Containerization
- **Gunicorn** - WSGI server

## Project Structure

```
QuarryDepthFinder/
├── main.py                    # Flask app factory
├── run.py                     # Application entry point
├── routes.py                  # Main API routes
├── advanced_routes.py         # Advanced feature routes
├── test_depth.py              # Test and demo routes
├── depth_analysis.py          # Depth calculation algorithms
├── volume_calculator.py       # Volume estimation logic
├── slope_analysis.py          # Slope analysis functions
├── raster.py                  # Raster data handling
├── three_visualization.py     # 3D model generation
├── report_generator.py        # PDF report creation
├── extraFunctions.py          # Utility functions
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── static/                    # CSS, JS, images
├── templates/                 # HTML templates
├── dem_tile.tif              # Sample DEM data
├── cropped.tif               # Sample cropped DEM
└── 3d/                        # 3D visualization files
```

## Installation

### Prerequisites
- Python 3.11+
- MongoDB (or MongoDB Atlas)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/Vishweswarann/QuarryDepthFinder.git
cd QuarryDepthFinder
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export MONGO_URI="mongodb://localhost:27017/QuarryDepthFinder"
# Or for MongoDB Atlas:
# export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/QuarryDepthFinder"
```

5. **Run the application**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Docker Setup

1. **Build the Docker image**
```bash
docker build -t quarry-depth-finder .
```

2. **Run the container**
```bash
docker run -p 8080:8080 \
  -e MONGO_URI="mongodb://your-mongodb-uri" \
  quarry-depth-finder
```

The application will be available at `http://localhost:8080`

## API Endpoints

### Main Routes (`/routes.py`)
- `GET /` - Home page
- `POST /upload-dem` - Upload DEM file
- `POST /analyze` - Analyze uploaded DEM
- `GET /results/<id>` - Retrieve analysis results
- `GET /history` - Get analysis history

### Advanced Routes (`/advanced_routes.py`)
- `POST /advanced/depth-profile` - Advanced depth profile analysis
- `POST /advanced/volume-comparison` - Compare volumes across areas
- `POST /advanced/slope-risk` - Slope stability risk assessment
- `POST /advanced/export-report` - Export analysis as PDF

### Test Routes (`/test_depth.py`)
- `GET /test` - Test interface
- `POST /test/calculate` - Test depth calculation
- `GET /test/sample` - Sample DEM data

## Key Modules

### depth_analysis.py
Performs core depth analysis on DEM data:
- Identifies quarry boundaries
- Calculates depth profiles
- Compares elevation differences

### volume_calculator.py
Estimates excavation volumes:
- Calculates volume from depth and area
- Supports multiple calculation methods
- Handles irregular geometries

### slope_analysis.py
Analyzes terrain slopes:
- Calculates slope angles
- Identifies risk zones
- Provides stability metrics

### three_visualization.py
Generates 3D visualizations:
- Creates Three.js models
- Renders terrain meshes
- Exports interactive 3D views

### report_generator.py
Creates comprehensive PDF reports:
- Includes maps and visualizations
- Provides statistical summaries
- Exports analysis results

## Usage Examples

### Basic Depth Analysis
```python
from depth_analysis import analyze_dem
import rasterio

# Load DEM data
with rasterio.open('dem_tile.tif') as src:
    dem_data = src.read(1)

# Analyze depth
results = analyze_dem(dem_data)
print(f"Maximum depth: {results['max_depth']} meters")
```

### Volume Calculation
```python
from volume_calculator import calculate_volume

volume = calculate_volume(
    depth=45.5,
    area=10000,  # in square meters
    method='trapezoid'
)
print(f"Estimated volume: {volume} cubic meters")
```

### Generate Report
```python
from report_generator import generate_pdf_report

generate_pdf_report(
    analysis_results=results,
    output_path='quarry_report.pdf',
    title='Quarry Depth Analysis Report'
)
```

## Sample Data

The repository includes sample DEM files:
- `dem_tile.tif` - Full DEM tile sample
- `cropped.tif` - Cropped area for quick testing

## Web Interface

The application provides a user-friendly web interface for:
- Uploading DEM files (GeoTIFF, ASCII Grid)
- Configuring analysis parameters
- Viewing 3D terrain visualizations
- Downloading generated reports
- Viewing analysis history

## Database Schema

### Analysis Collection
```json
{
  "_id": ObjectId,
  "filename": "dem_tile.tif",
  "upload_date": ISODate,
  "bounds": {
    "north": 0.0,
    "south": 0.0,
    "east": 0.0,
    "west": 0.0
  },
  "results": {
    "max_depth": 45.5,
    "avg_depth": 22.3,
    "total_volume": 234567.89,
    "area": 10000
  },
  "metadata": {}
}
```

## Performance Considerations

- Handles large DEM files efficiently with streaming
- Supports multiple coordinate systems via PyProj
- Optimized raster operations using NumPy/SciPy
- Caching of processed results in MongoDB
- Asynchronous report generation

## Limitations

- Maximum DEM file size: 2GB (configurable)
- Requires valid GeoTIFF or ASCII Grid format
- MongoDB connection required for persistent storage
- 3D visualization limited to browser capabilities

## Future Enhancements

- Real-time streaming analysis
- Machine learning-based boundary detection
- Multi-file comparison and analysis
- API rate limiting and authentication
- Advanced ground stability modeling
- Integration with satellite imagery
- Mobile application support
- Real-time monitoring dashboard
- Automated report scheduling

## Dependencies

See `requirements.txt` for complete list:
- Flask 3.0.2
- Rasterio 1.4.0
- NumPy 2.1.0+
- SciPy 1.14.0+
- PyProj 3.6.1
- Matplotlib 3.9.0+
- FPDF 1.7.2
- Gunicorn 21.2.0

## Configuration

### Environment Variables
```bash
MONGO_URI          # MongoDB connection string
FLASK_ENV          # development/production
DEBUG              # Enable debug mode
MAX_FILE_SIZE      # Maximum upload size (default: 2GB)
```

### Flask Configuration
Edit `main.py` to customize:
- Secret key
- MongoDB URI
- Upload folders
- Report generation settings

## Troubleshooting

**MongoDB Connection Error**
```bash
# Ensure MongoDB is running
# Update MONGO_URI environment variable
export MONGO_URI="mongodb://localhost:27017/QuarryDepthFinder"
```

**Missing Rasterio Dependencies**
```bash
# Install system dependencies
apt-get install libgdal-dev g++
pip install --no-cache-dir rasterio
```

**3D Visualization Not Loading**
- Clear browser cache
- Check browser console for errors
- Ensure WebGL is enabled

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Open source

## Author

Vishweswarann

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the project maintainer.

## Acknowledgments

- Built with geospatial processing libraries: Rasterio, PyProj, GDAL
- 3D visualization powered by Three.js
- Scientific computing with NumPy and SciPy
- PDF generation using FPDF
