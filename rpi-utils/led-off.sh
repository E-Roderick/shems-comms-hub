#!/bin/bash

echo 0 | sudo tee /sys/class/leds/ACT/brightness
echo 0 | sudo tee /sys/class/leds/PWR/brightness
