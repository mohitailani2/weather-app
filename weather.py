import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime, timedelta
import threading
from PIL import Image, ImageTk
import io
import base64

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ Weather Forecast App")
        self.root.geometry("800x700")
        self.root.configure(bg='#74b9ff')
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       background='#74b9ff',
                       foreground='white')
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12),
                       background='#74b9ff',
                       foreground='white')
        
        style.configure('Custom.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Weather.TLabel',
                       font=('Segoe UI', 14),
                       background='white',
                       foreground='#2d3436')
        
        style.configure('Temp.TLabel',
                       font=('Segoe UI', 32, 'bold'),
                       background='white',
                       foreground='#74b9ff')
        
        style.configure('Forecast.TLabel',
                       font=('Segoe UI', 10),
                       background='#f8f9fa',
                       foreground='#2d3436')
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#74b9ff', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#74b9ff')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🌤️ Weather Forecast", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Get current weather and 5-day forecast", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Input section
        input_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=20)
        input_frame.pack(fill='x', pady=(0, 20))
        
        # City input
        tk.Label(input_frame, text="City Name:", font=('Segoe UI', 11), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.city_entry = tk.Entry(input_frame, font=('Segoe UI', 11), width=25, relief='flat', bd=5)
        self.city_entry.grid(row=0, column=1, padx=(0, 10), sticky='ew')
        
        # API Key input
        tk.Label(input_frame, text="API Key:", font=('Segoe UI', 11), bg='white').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.api_entry = tk.Entry(input_frame, font=('Segoe UI', 11), width=25, show='*', relief='flat', bd=5)
        self.api_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky='ew')
        
        # Search button
        self.search_btn = tk.Button(input_frame, text="🔍 Get Weather", 
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#00b894', fg='white',
                                   relief='flat', padx=20, pady=10,
                                   cursor='hand2',
                                   command=self.get_weather_threaded)
        self.search_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky='ns')
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        
        # API help
        help_label = tk.Label(input_frame, text="💡 Get free API key at openweathermap.org/api", 
                             font=('Segoe UI', 9), bg='white', fg='#636e72')
        help_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        # Current weather section
        self.current_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=20)
        self.current_frame.pack(fill='x', pady=(0, 20))
        self.current_frame.pack_forget()  # Hide initially
        
        # Forecast section
        self.forecast_frame = ttk.Frame(main_frame, style='Custom.TFrame', padding=20)
        self.forecast_frame.pack(fill='both', expand=True)
        self.forecast_frame.pack_forget()  # Hide initially
        
        # Bind Enter key
        self.city_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        self.api_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        
        # Focus on city entry
        self.city_entry.focus()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def get_weather_threaded(self):
        """Run weather fetch in separate thread to prevent GUI freezing"""
        city = self.city_entry.get().strip()
        api_key = self.api_entry.get().strip()
        
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        # Disable button and show loading
        self.search_btn.config(state='disabled', text='⏳ Loading...')
        
        # Run in thread
        thread = threading.Thread(target=self.get_weather, args=(city, api_key))
        thread.daemon = True
        thread.start()
    
    def get_weather(self, city, api_key):
        """Fetch weather data from API"""
        try:
            # Get current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather"
            current_params = {'q': city, 'appid': api_key, 'units': 'metric'}
            current_response = requests.get(current_url, params=current_params, timeout=10)
            
            if current_response.status_code != 200:
                error_data = current_response.json()
                raise Exception(error_data.get('message', 'Failed to fetch weather data'))
            
            current_data = current_response.json()
            
            # Get 5-day forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {'q': city, 'appid': api_key, 'units': 'metric'}
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
            
            if forecast_response.status_code != 200:
                error_data = forecast_response.json()
                raise Exception(error_data.get('message', 'Failed to fetch forecast data'))
            
            forecast_data = forecast_response.json()
            
            # Update GUI in main thread
            self.root.after(0, self.display_weather_data, current_data, forecast_data)
            
        except requests.exceptions.Timeout:
            self.root.after(0, self.show_error, "Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            self.root.after(0, self.show_error, "No internet connection. Please check your network.")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.search_btn.config(state='normal', text='🔍 Get Weather'))
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def display_weather_data(self, current_data, forecast_data):
        """Display weather data in GUI"""
        self.display_current_weather(current_data)
        self.display_forecast(forecast_data)
    
    def display_current_weather(self, data):
        """Display current weather information"""
        # Clear existing widgets
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        
        # City name and country
        city_label = ttk.Label(self.current_frame, 
                              text=f"{data['name']}, {data['sys']['country']}", 
                              font=('Segoe UI', 18, 'bold'),
                              background='white')
        city_label.pack(pady=(0, 10))
        
        # Current temperature
        temp_label = ttk.Label(self.current_frame, 
                              text=f"{round(data['main']['temp'])}°C",
                              style='Temp.TLabel')
        temp_label.pack(pady=(0, 5))
        
        # Weather description
        desc_label = ttk.Label(self.current_frame,
                              text=data['weather'][0]['description'].title(),
                              font=('Segoe UI', 14),
                              background='white')
        desc_label.pack(pady=(0, 20))
        
        # Details grid
        details_frame = tk.Frame(self.current_frame, bg='white')
        details_frame.pack(fill='x')
        
        details = [
            ("Feels Like", f"{round(data['main']['feels_like'])}°C"),
            ("Humidity", f"{data['main']['humidity']}%"),
            ("Wind Speed", f"{data['wind']['speed']} m/s"),
            ("Pressure", f"{data['main']['pressure']} hPa")
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            detail_frame = tk.Frame(details_frame, bg='#f8f9fa', relief='flat', bd=1)
            detail_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(detail_frame, text=label, font=('Segoe UI', 10), 
                    bg='#f8f9fa', fg='#636e72').pack(pady=(5, 0))
            tk.Label(detail_frame, text=value, font=('Segoe UI', 12, 'bold'), 
                    bg='#f8f9fa', fg='#2d3436').pack(pady=(0, 5))
        
        # Configure grid weights
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)
        
        self.current_frame.pack(fill='x', pady=(0, 20))
    
    def display_forecast(self, data):
        """Display 5-day forecast"""
        # Clear existing widgets
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        
        # Title
        forecast_title = ttk.Label(self.forecast_frame,
                                  text="5-Day Forecast",
                                  font=('Segoe UI', 16, 'bold'),
                                  background='white')
        forecast_title.pack(pady=(0, 20))
        
        # Process forecast data - group by day
        daily_forecasts = {}
        
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'temps': [],
                    'weather': item['weather'][0],
                    'dt': item['dt']
                }
            
            daily_forecasts[date]['temps'].append(item['main']['temp'])
        
        # Get first 5 days
        forecast_days = list(daily_forecasts.items())[:5]
        
        # Create forecast grid
        forecast_grid = tk.Frame(self.forecast_frame, bg='white')
        forecast_grid.pack(fill='both', expand=True)
        
        for i, (date, day_data) in enumerate(forecast_days):
            # Calculate temperatures
            max_temp = round(max(day_data['temps']))
            min_temp = round(min(day_data['temps']))
            
            # Determine day name
            today = datetime.now().date()
            if date == today:
                day_name = "Today"
            elif date == today + timedelta(days=1):
                day_name = "Tomorrow"
            else:
                day_name = date.strftime("%A")
            
            # Create forecast card
            card_frame = tk.Frame(forecast_grid, bg='#f8f9fa', relief='solid', bd=1)
            card_frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='ew')
            
            # Day name
            day_label = tk.Label(card_frame, text=day_name,
                               font=('Segoe UI', 12, 'bold'),
                               bg='#f8f9fa', fg='#2d3436')
            day_label.pack(pady=(10, 5))
            
            # Weather icon (emoji)
            icon = self.get_weather_emoji(day_data['weather']['icon'])
            icon_label = tk.Label(card_frame, text=icon, font=('Segoe UI', 24),
                                bg='#f8f9fa')
            icon_label.pack(pady=5)
            
            # Temperature
            temp_label = tk.Label(card_frame, text=f"{max_temp}° / {min_temp}°",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#f8f9fa', fg='#74b9ff')
            temp_label.pack(pady=5)
            
            # Description
            desc_label = tk.Label(card_frame, text=day_data['weather']['description'].title(),
                                font=('Segoe UI', 9),
                                bg='#f8f9fa', fg='#636e72',
                                wraplength=120)
            desc_label.pack(pady=(0, 10))
        
        # Configure grid weights
        for i in range(3):
            forecast_grid.columnconfigure(i, weight=1)
        
        self.forecast_frame.pack(fill='both', expand=True)
    
    def get_weather_emoji(self, icon_code):
        """Convert weather icon code to emoji"""
        emoji_map = {
            '01d': '☀️', '01n': '🌙',  # clear sky
            '02d': '⛅', '02n': '☁️',  # few clouds
            '03d': '☁️', '03n': '☁️',  # scattered clouds
            '04d': '☁️', '04n': '☁️',  # broken clouds
            '09d': '🌧️', '09n': '🌧️',  # shower rain
            '10d': '🌦️', '10n': '🌧️',  # rain
            '11d': '⛈️', '11n': '⛈️',  # thunderstorm
            '13d': '❄️', '13n': '❄️',  # snow
            '50d': '🌫️', '50n': '🌫️'   # mist
        }
        return emoji_map.get(icon_code, '🌤️')
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#74b9ff', padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#74b9ff')
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🌤️ Weather Forecast", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Get current weather and 5-day forecast for any city", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(8, 0))
        
        # Input section with rounded appearance
        input_container = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
        input_container.pack(fill='x', pady=(0, 25))
        
        input_frame = tk.Frame(input_container, bg='white', padx=25, pady=25)
        input_frame.pack(fill='x')
        
        # City input row
        city_row = tk.Frame(input_frame, bg='white')
        city_row.pack(fill='x', pady=(0, 15))
        
        tk.Label(city_row, text="🏙️ City:", font=('Segoe UI', 11, 'bold'), bg='white', fg='#2d3436').pack(side='left')
        self.city_entry = tk.Entry(city_row, font=('Segoe UI', 11), width=30, relief='solid', bd=1)
        self.city_entry.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # API key input row
        api_row = tk.Frame(input_frame, bg='white')
        api_row.pack(fill='x', pady=(0, 20))
        
        tk.Label(api_row, text="🔑 API Key:", font=('Segoe UI', 11, 'bold'), bg='white', fg='#2d3436').pack(side='left')
        self.api_entry = tk.Entry(api_row, font=('Segoe UI', 11), width=30, show='*', relief='solid', bd=1)
        self.api_entry.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Button row
        button_row = tk.Frame(input_frame, bg='white')
        button_row.pack(fill='x')
        
        self.search_btn = tk.Button(button_row, text="🔍 Get Weather Forecast", 
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#00b894', fg='white',
                                   relief='flat', padx=30, pady=12,
                                   cursor='hand2',
                                   command=self.get_weather_threaded)
        self.search_btn.pack(side='left')
        
        # Help text
        help_label = tk.Label(input_frame, text="💡 Get your free API key at openweathermap.org/api", 
                             font=('Segoe UI', 9), bg='white', fg='#74b9ff')
        help_label.pack(pady=(15, 0))
        
        # Current weather section (initially hidden)
        self.current_frame = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
        
        # Forecast section (initially hidden)
        self.forecast_frame = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
        
        # Bind Enter key to both inputs
        self.city_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        self.api_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        
        # Set placeholder text
        self.city_entry.insert(0, "e.g., London, New York, Tokyo")
        self.city_entry.bind('<FocusIn>', self.clear_placeholder)
        
        # Focus on city entry
        self.city_entry.focus()
    
    def clear_placeholder(self, event):
        """Clear placeholder text when focused"""
        if self.city_entry.get() == "e.g., London, New York, Tokyo":
            self.city_entry.delete(0, tk.END)
    
    def get_weather_threaded(self):
        """Run weather fetch in separate thread"""
        city = self.city_entry.get().strip()
        api_key = self.api_entry.get().strip()
        
        # Clear placeholder if still there
        if city == "e.g., London, New York, Tokyo":
            city = ""
        
        if not city:
            messagebox.showerror("Input Error", "Please enter a city name")
            self.city_entry.focus()
            return
        
        if not api_key:
            messagebox.showerror("Input Error", "Please enter your OpenWeatherMap API key")
            self.api_entry.focus()
            return
        
        # Update button state
        self.search_btn.config(state='disabled', text='⏳ Fetching Weather...', bg='#b2bec3')
        
        # Run API call in separate thread
        thread = threading.Thread(target=self.fetch_weather_data, args=(city, api_key))
        thread.daemon = True
        thread.start()
    
    def fetch_weather_data(self, city, api_key):
        """Fetch weather data from OpenWeatherMap API"""
        try:
            # Current weather API call
            current_url = "https://api.openweathermap.org/data/2.5/weather"
            current_params = {'q': city, 'appid': api_key, 'units': 'metric'}
            
            current_response = requests.get(current_url, params=current_params, timeout=15)
            
            if current_response.status_code == 401:
                raise Exception("Invalid API key. Please check your OpenWeatherMap API key.")
            elif current_response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the spelling.")
            elif current_response.status_code != 200:
                error_data = current_response.json()
                raise Exception(error_data.get('message', 'Failed to fetch current weather'))
            
            current_data = current_response.json()
            
            # 5-day forecast API call
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {'q': city, 'appid': api_key, 'units': 'metric'}
            
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=15)
            
            if forecast_response.status_code != 200:
                error_data = forecast_response.json()
                raise Exception(error_data.get('message', 'Failed to fetch forecast'))
            
            forecast_data = forecast_response.json()
            
            # Update GUI on main thread
            self.root.after(0, self.update_weather_display, current_data, forecast_data)
            
        except requests.exceptions.Timeout:
            self.root.after(0, self.show_error, "Request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            self.root.after(0, self.show_error, "Connection error. Please check your internet connection.")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            # Reset button
            self.root.after(0, self.reset_search_button)
    
    def reset_search_button(self):
        """Reset search button to original state"""
        self.search_btn.config(state='normal', text='🔍 Get Weather Forecast', bg='#00b894')
    
    def update_weather_display(self, current_data, forecast_data):
        """Update the weather display with fetched data"""
        self.show_current_weather(current_data)
        self.show_forecast(forecast_data)
    
    def show_current_weather(self, data):
        """Display current weather in a beautiful card"""
        # Clear previous data
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        
        # Current weather card
        current_card = tk.Frame(self.current_frame, bg='white', padx=30, pady=25)
        current_card.pack(fill='x')
        
        # Location
        location_label = tk.Label(current_card, 
                                 text=f"📍 {data['name']}, {data['sys']['country']}", 
                                 font=('Segoe UI', 16, 'bold'),
                                 bg='white', fg='#2d3436')
        location_label.pack(pady=(0, 15))
        
        # Main temperature display
        temp_frame = tk.Frame(current_card, bg='white')
        temp_frame.pack(pady=(0, 20))
        
        # Weather icon
        icon = self.get_weather_emoji(data['weather'][0]['icon'])
        icon_label = tk.Label(temp_frame, text=icon, font=('Segoe UI', 48), bg='white')
        icon_label.pack(side='left', padx=(0, 20))
        
        # Temperature and description
        temp_info = tk.Frame(temp_frame, bg='white')
        temp_info.pack(side='left')
        
        temp_label = tk.Label(temp_info, text=f"{round(data['main']['temp'])}°C",
                             font=('Segoe UI', 36, 'bold'),
                             bg='white', fg='#74b9ff')
        temp_label.pack(anchor='w')
        
        desc_label = tk.Label(temp_info, text=data['weather'][0]['description'].title(),
                             font=('Segoe UI', 14),
                             bg='white', fg='#636e72')
        desc_label.pack(anchor='w')
        
        # Weather details
        details_container = tk.Frame(current_card, bg='white')
        details_container.pack(fill='x', pady=(20, 0))
        
        details = [
            ("🌡️ Feels Like", f"{round(data['main']['feels_like'])}°C"),
            ("💧 Humidity", f"{data['main']['humidity']}%"),
            ("💨 Wind Speed", f"{data['wind']['speed']} m/s"),
            ("📊 Pressure", f"{data['main']['pressure']} hPa")
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            detail_card = tk.Frame(details_container, bg='#f1f3f4', relief='flat', bd=0)
            detail_card.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
            
            tk.Label(detail_card, text=label, font=('Segoe UI', 10), 
                    bg='#f1f3f4', fg='#636e72').pack(pady=(8, 2))
            tk.Label(detail_card, text=value, font=('Segoe UI', 12, 'bold'), 
                    bg='#f1f3f4', fg='#2d3436').pack(pady=(0, 8))
        
        # Configure grid
        details_container.columnconfigure(0, weight=1)
        details_container.columnconfigure(1, weight=1)
        
        self.current_frame.pack(fill='x', pady=(0, 25))
    
    def show_forecast(self, data):
        """Display 5-day forecast in cards"""
        # Clear previous forecast
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        
        # Forecast title
        title_frame = tk.Frame(self.forecast_frame, bg='white', pady=15)
        title_frame.pack(fill='x')
        
        forecast_title = tk.Label(title_frame, text="📅 5-Day Forecast",
                                 font=('Segoe UI', 18, 'bold'),
                                 bg='white', fg='#2d3436')
        forecast_title.pack()
        
        # Process forecast data
        daily_data = {}
        today = datetime.now().date()
        
        for item in data['list']:
            forecast_date = datetime.fromtimestamp(item['dt']).date()
            
            if forecast_date not in daily_data:
                daily_data[forecast_date] = {
                    'temps': [],
                    'weather': item['weather'][0],
                    'dt': item['dt'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed']
                }
            
            daily_data[forecast_date]['temps'].append(item['main']['temp'])
        
        # Get next 5 days
        forecast_days = sorted(daily_data.items())[:5]
        
        # Create scrollable forecast container
        forecast_container = tk.Frame(self.forecast_frame, bg='white')
        forecast_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create forecast cards
        for i, (date, day_data) in enumerate(forecast_days):
            max_temp = round(max(day_data['temps']))
            min_temp = round(min(day_data['temps']))
            avg_temp = round(sum(day_data['temps']) / len(day_data['temps']))
            
            # Determine day name
            if date == today:
                day_name = "Today"
            elif date == today + timedelta(days=1):
                day_name = "Tomorrow"
            else:
                day_name = date.strftime("%A")
            
            date_str = date.strftime("%b %d")
            
            # Forecast card
            card = tk.Frame(forecast_container, bg='#f8f9fa', relief='solid', bd=1, padx=15, pady=15)
            card.pack(fill='x', pady=5)
            
            # Card content
            card_content = tk.Frame(card, bg='#f8f9fa')
            card_content.pack(fill='x')
            
            # Left side - Day info
            left_info = tk.Frame(card_content, bg='#f8f9fa')
            left_info.pack(side='left', fill='x', expand=True)
            
            # Day name and date
            day_label = tk.Label(left_info, text=f"{day_name} • {date_str}",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#f8f9fa', fg='#2d3436')
            day_label.pack(anchor='w')
            
            # Weather description
            desc_label = tk.Label(left_info, text=day_data['weather']['description'].title(),
                                font=('Segoe UI', 10),
                                bg='#f8f9fa', fg='#636e72')
            desc_label.pack(anchor='w', pady=(2, 0))
            
            # Center - Weather icon
            icon_frame = tk.Frame(card_content, bg='#f8f9fa')
            icon_frame.pack(side='left', padx=20)
            
            icon = self.get_weather_emoji(day_data['weather']['icon'])
            icon_label = tk.Label(icon_frame, text=icon, font=('Segoe UI', 32), bg='#f8f9fa')
            icon_label.pack()
            
            # Right side - Temperature
            temp_frame = tk.Frame(card_content, bg='#f8f9fa')
            temp_frame.pack(side='right')
            
            temp_label = tk.Label(temp_frame, text=f"{max_temp}°",
                                font=('Segoe UI', 20, 'bold'),
                                bg='#f8f9fa', fg='#74b9ff')
            temp_label.pack(anchor='e')
            
            min_temp_label = tk.Label(temp_frame, text=f"{min_temp}°",
                                    font=('Segoe UI', 14),
                                    bg='#f8f9fa', fg='#636e72')
            min_temp_label.pack(anchor='e')
        
        self.forecast_frame.pack(fill='both', expand=True)
    
    def show_error(self, message):
        """Display error message to user"""
        messagebox.showerror("Weather Error", message)
    
    def center_window(self):
        """Center the application window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')


def main():
    """Create and run the weather application"""
    root = tk.Tk()
    app = WeatherApp(root)
    
    # Set minimum window size
    root.minsize(600, 500)
    
    # Configure window icon (if you have one)
    try:
        # You can add an .ico file here if you have one
        # root.iconbitmap('weather_icon.ico')
        pass
    except:
        pass
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    print("🌤️ Starting Weather Forecast App...")
    print("💡 Get your free API key from: https://openweathermap.org/api")
    main()
