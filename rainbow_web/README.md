# RainbowSim - Interactive Physics Simulator

An interactive web-based physics simulator for light phenomena using Pygame and Pygbag.

## Features

- **Refraction**: Visualize light bending through different media
- **Prism**: See light dispersion through prisms
- **Realistic Ray Tracing**: Fresnel equations and realistic light behavior
- **Ray Paths in Droplets**: Understand light paths in water droplets
- **Water Droplets**: Full droplet simulation with internal reflection
- **Rainbow Formation**: Observe rainbow formation from sunlight and water droplets

## Quick Start

### Run Locally

```bash
cd rainbow_web
python main.py
```

### Build for Web

```bash
pip install pygbag
pygbag main.py --build web
python -m http.server 8000 --directory web
```

Then open http://localhost:8000 in your browser.

### Deploy

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed deployment guides to Railway, Heroku, or GitHub Pages.

## Project Structure

```
rainbow_web/
├── main.py              # Main application with menu system
├── refraction.py        # Refraction visualization
├── prism.py            # Prism simulation
├── raytrace.py         # Realistic ray tracing
├── droplet.py          # Ray path visualization in droplets
├── droplet2.py         # Full droplet simulation
├── rainbow.py          # Rainbow formation simulation
├── pyproject.toml      # Build configuration for Pygbag
├── requirements.txt    # Python dependencies
├── BUILD_INSTRUCTIONS.md # Deployment guide
└── build/              # Build artifacts
    └── web/            # Web build output
```

## Interactive Features

Once you click on a simulation:

- **Mouse Controls**: Interact with simulations (varies by module)
- **Keyboard Controls**: Adjust parameters (check each simulation for specific keys)
- **Responsive Design**: Works on different screen sizes
- **Real-time Animation**: Live parameter adjustments

## Technology Stack

- **Pygame**: 2D graphics and physics simulation
- **Pygbag**: Pygame to WebAssembly compiler
- **Javascript/WebGL**: Browser rendering

## Requirements

- Python 3.8+
- Pygame 2.1+
- Pygbag 0.7.3+

## Troubleshooting

**Canvas not showing?**
- Check browser console (F12) for errors
- Ensure you're using a modern browser (Chrome, Firefox, Safari, Edge)

**Slow performance?**
- Reduce simulation complexity
- Run built (minified) version: `pygbag main.py --build web --minify`

**Modules not loading?**
- Ensure all .py files are in the same directory
- Check that imports are correct

## Architecture Notes

- Each simulation module can run independently
- Asyncio is used for browser event loop compatibility
- Pygame display updates work in web browsers via Pygbag

## Future Enhancements

- [ ] Add parameter sliders for interactive adjustment
- [ ] Add presets for different scenarios
- [ ] Record and share simulation results
- [ ] Add physics formulas and explanations
- [ ] Mobile touch controls

## License

[Add your license here]

## Author

Created with Pygame and Pygbag

---

**Ready to deploy?** See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
