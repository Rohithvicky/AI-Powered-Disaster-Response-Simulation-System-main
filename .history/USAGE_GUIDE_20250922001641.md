# AI Disaster Response Simulation System - Usage Guide

## 🚀 Quick Start

1. **Start the Server**: The server is already running at `http://localhost:8000`
2. **Open the Dashboard**: Navigate to `http://localhost:8000` in your web browser
3. **Test the System**: Click "Test Sound" to verify audio is working

## 🎮 How to Use

### Control Panel
- **Start**: Begin the disaster simulation
- **Stop**: Stop the simulation
- **Reset**: Generate a new disaster scenario
- **Pause/Resume**: Pause or resume the simulation
- **Sound On/Off**: Toggle sound effects
- **Test Sound**: Test if audio is working (click this first!)

### Visual Elements
- **👨‍🚒 Orange squares**: Rescue team (moves toward victims)
- **🚨 Yellow squares**: Victims needing rescue
- **🚑 Blue squares**: Ambulances
- **🚒 Purple squares**: Fire trucks
- **🚁 Green squares**: Helicopters
- **🚤 Cyan squares**: Boats
- **🏥 White squares**: Medical supplies
- **🚜 Brown squares**: Heavy machinery
- **Gray squares**: Used resources (appear after rescue)

### Sound Effects
- **🚑 Ambulance**: Sawtooth wave sound
- **🚒 Fire Truck**: Square wave sound
- **🚁 Helicopter**: Triangle wave sound
- **🚤 Boat**: Low sine wave sound
- **🏥 Medical**: High sine wave sound
- **🚜 Machinery**: Low sawtooth wave sound
- **✅ Success**: Musical chord when rescue is successful

## 🔧 Troubleshooting

### Icons Not Showing
- The system now uses emoji icons instead of SVG files for better compatibility
- All icons should display immediately without loading issues

### Sound Not Working
1. Click "Test Sound" button first to initialize audio
2. Make sure your browser allows audio (check for audio permissions)
3. Try clicking anywhere on the page first (required for audio context)
4. Check if sound is enabled (Sound On/Off button)

### Server Issues
- If server stops, run: `python server.py`
- Check that port 8000 is not blocked
- Make sure all files are in the correct directory

## 🎯 What to Expect

1. **Start the simulation** - A disaster scenario will be generated
2. **Watch the rescue team move** - The orange rescuer will move toward yellow victims
3. **Listen for sounds** - Each resource type has a unique sound when used
4. **See used resources** - Gray squares appear where victims were rescued
5. **Check the AI decisions panel** - Shows what resources were used for each rescue

## 🌟 Features

- ✅ **Dark transparent grid** (no more white background)
- ✅ **Single moving rescuer** (no more multiple stationary rescuers)
- ✅ **Sound effects** for each resource type
- ✅ **Used resource visualization** at victim locations
- ✅ **Real-time AI decisions** showing rescue operations
- ✅ **Interactive tooltips** with detailed information

Enjoy the improved disaster response simulation! 🚨🚑🚒
