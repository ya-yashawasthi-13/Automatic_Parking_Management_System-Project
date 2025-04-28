# Smart Parking Management System

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-brightgreen.svg)](https://docs.python.org/3/library/tkinter.html)
[![Pillow](https://img.shields.io/badge/Image_Processing-Pillow-yellow.svg)](https://pillow.readthedocs.io/en/stable/)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME?style=social)](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME?style=social)](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME/network/members)
[![License](https://img.shields.io/github/license/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME)](LICENSE) ## Overview

The Smart Parking Management System is a comprehensive Python-based application designed to efficiently manage parking lots. Utilizing a graphical user interface built with Tkinter, it provides real-time monitoring of parking slot availability, simulates vehicle entry and exit processes (including ANPR simulation), manages waiting queues and priority exit stacks, calculates parking fees, and provides insightful statistics.

This project showcases the integration of various data structures (lists, deque, stack, dictionary, graph) and algorithms to solve a real-world problem. It also demonstrates GUI development with a modern look and feel, incorporating elements like tabbed interfaces, dynamic displays, and basic animation.

## Features

- **Real-time Parking Slot Status:** Visual representation of occupied and available parking slots.
- **Automated Vehicle Entry:** Simulates vehicle entry, assigns available slots, and generates random license plates.
- **Waiting Queue Management:** Handles vehicles when the parking lot is full using a First-In, First-Out (FIFO) queue.
- **Priority Exit Stack:** Implements a Last-In, First-Out (LIFO) stack for managing priority exits in compact areas.
- **ANPR Camera Simulation:** Provides a visual simulation of Automatic Number Plate Recognition during entry.
- **Manual Vehicle Control:** Allows manual entry and exit of vehicles through the GUI.
- **Fee Calculation:** Calculates parking fees based on vehicle type and parking duration.
- **Comprehensive Statistics:** Displays real-time statistics such as total entries, exits, current occupancy, peak occupancy, average stay time, and total revenue.
- **Activity Logging:** Records recent and full activity logs for monitoring system operations.
- **Settings Configuration:** Enables users to adjust the total number of parking slots and customize the fee structure based on vehicle types.
- **Automation Simulation:** Option to automate vehicle entries and exits at configurable rates for testing and demonstration.
- **Dynamic Visualization:** Updates the parking map, entry queue, and exit stack displays in real-time.
- **Modern GUI:** User-friendly interface with a tabbed layout for easy navigation and information access.

## Technologies Used

- **Python 3.x:** The core programming language.
- **Tkinter:** Python's standard GUI library for creating the user interface.
- **Pillow (PIL):** Used for image handling (though the current implementation doesn't actively load a Figma design, it's included as a potential future enhancement).
- **`time`:** For simulating real-time events and tracking durations.
- **`random`:** For generating random data like license plates, vehicle types, and colors.
- **`string`:** For generating random license plate characters.
- **`threading`:** Used for running the automation simulation in the background without blocking the GUI.
- **`collections.deque`:** Implemented for the entry queue and activity logs (efficient for appends and pops from both ends).
- **`math`:** Used for layout calculations in the parking map visualization.
