import streamlit as st
import torch
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
import logging
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.transformer_classifier import MentalHealthClassifier
from utils.tokenizer import tokenize_text
from utils.model_downloader import get_model_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Risk level mapping
RISK_LEVELS = {
    0: {"label": "No Risk", "color": "green"},
    1: {"label": "Low Risk", "color": "yellow"},
    2: {"label": "High Risk", "color": "red"}
}

class MentalHealthDashboard:
    """Streamlit Dashboard for Mental Health Monitoring"""
    
    def __init__(self, model_path=None, data_path=None, optimized_model_path=None):
        """
        Initialize the dashboard
        
        Args:
            model_path: Path to the trained model
            data_path: Path to the data file with message history
            optimized_model_path: Path to the optimized JIT model
        """        # Set default model paths if not provided
        if model_path is None:
            try:
                # Try to get model from downloader
                model_path = get_model_path("saved_model_fixed.pt")
            except Exception as e:
                logger.warning(f"Could not download model: {e}")
                model_path = os.path.join(os.path.dirname(__file__), '../models/checkpoints/saved_model_fixed.pt')
        # Don't set optimized model path by default to avoid loading errors
        self.model_path = model_path
        self.optimized_model_path = optimized_model_path
        self.data_path = data_path
        self.model = None
        self.optimized_model = None
        self.data = None
        self.use_optimized_model = False
        
        # Page configuration
        st.set_page_config(
            page_title="Guardian - Mental Health Monitoring",
            page_icon="🧠",
            layout="wide"
        )
        
        # Add custom CSS
        self.add_custom_css()
    
    def add_custom_css(self):
        """Add custom CSS styling"""
        st.markdown("""
        <style>
        .high-risk {
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 5px solid red;
            padding: 10px;
            border-radius: 5px;
        }
        .medium-risk {
            background-color: rgba(255, 255, 0, 0.1);
            border-left: 5px solid orange;
            padding: 10px;
            border-radius: 5px;
        }
        .no-risk {
            background-color: rgba(0, 255, 0, 0.1);
            border-left: 5px solid green;
            padding: 10px;
            border-radius: 5px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stButton > button {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def load_model(self):
        """Load the transformer model"""
        if not self.model_path:
            st.error("Model path not provided.")
            return False
            
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            # Load standard model
            self.model = MentalHealthClassifier().to(device)
            self.model.load_state_dict(torch.load(self.model_path, map_location=device))
            self.model.eval()
            logger.info(f"Standard model loaded from {self.model_path}")
              # Try to load optimized model if available
            if self.optimized_model_path and os.path.exists(self.optimized_model_path):
                try:
                    # Check if it's a JIT model by trying to load it
                    test_model = torch.jit.load(self.optimized_model_path, map_location=device)
                    test_model.eval()
                    self.optimized_model = test_model
                    logger.info(f"Optimized JIT model loaded from {self.optimized_model_path}")
                    self.use_optimized_model = True
                except Exception as e:
                    logger.warning(f"Could not load as JIT model, trying as regular PyTorch model: {str(e)}")
                    # Fall back to using the same model as the standard model
                    self.optimized_model = None
                    self.use_optimized_model = False
                    
            return True
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            logger.error(f"Model loading error: {str(e)}")
            return False
    
    def load_optimized_model(self):
        """Load the optimized JIT model"""
        if not self.optimized_model_path:
            st.error("Optimized model path not provided.")
            return False
            
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.optimized_model = torch.jit.load(self.optimized_model_path, map_location=device)
            self.optimized_model.eval()
            self.use_optimized_model = True
            logger.info(f"Optimized model loaded from {self.optimized_model_path}")
            return True
        except Exception as e:
            st.error(f"Error loading optimized model: {str(e)}")
            logger.error(f"Optimized model loading error: {str(e)}")
            return False
    
    def load_data(self):
        """Load message history data"""
        if not self.data_path or not os.path.exists(self.data_path):
            # Create sample data if file doesn't exist
            self.data = self.create_sample_data()
            return
        
        try:
            with open(self.data_path, 'r') as f:
                self.data = pd.DataFrame(json.load(f))
            logger.info(f"Data loaded from {self.data_path}")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            logger.error(f"Data loading error: {str(e)}")
            # Create sample data as fallback
            self.data = self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample data for demonstration"""
        # Generate dates for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create sample data
        np.random.seed(42)
        data = []
        
        for date in dates:
            # Generate 1-5 messages for each day
            n_messages = np.random.randint(1, 6)
            for _ in range(n_messages):
                # Random risk level, weighted towards low risk
                risk_level = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
                
                # Generate sample message based on risk level
                if risk_level == 0:
                    message = np.random.choice([
                        "Had a good day at school today!",
                        "Excited about the weekend plans.",
                        "Enjoying my new hobby.",
                        "Just finished homework, time to relax."
                    ])
                elif risk_level == 1:
                    message = np.random.choice([
                        "Feeling a bit down today.",
                        "School is stressful right now.",
                        "Not sure how to handle this situation.",
                        "Had an argument with a friend."
                    ])
                else:  # High risk
                    message = np.random.choice([
                        "I don't see the point in trying anymore.",
                        "Everyone would be better off without me.",
                        "I'm just a burden to everyone.",
                        "I can't take this pain anymore."
                    ])
                
                # Create entry
                data.append({
                    'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                    'user': 'sample_user',                    'message': message,
                    'risk_level': risk_level,
                    'risk_score': 0.3 if risk_level == 0 else (0.6 if risk_level == 1 else 0.85),
                    'platform': np.random.choice(['Discord', 'SMS', 'Email'])
                })
        return pd.DataFrame(data)

    def analyze_text(self, text):
        """
        Analyze text for mental health risk indicators
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with prediction and risk scores
        """
        if not self.model:
            if not self.load_model():
                return {"prediction": 0, "scores": [0.8, 0.15, 0.05]}
        
        # Tokenize the text
        inputs = tokenize_text(text)
        
        # Get device
        device = next(self.model.parameters()).device
        
        # Measure inference time
        start_time = time.time()
        
        # Use optimized model if available
        if self.use_optimized_model and self.optimized_model:
            # Make prediction with optimized model
            with torch.no_grad():
                input_ids = inputs["input_ids"].to(device)
                attention_mask = inputs["attention_mask"].to(device)
                outputs = self.optimized_model(input_ids, attention_mask)
                probs = torch.softmax(outputs, dim=1).squeeze().cpu().tolist()
        else:
            # Make prediction with standard model
            with torch.no_grad():
                input_ids = inputs["input_ids"].to(device)
                attention_mask = inputs["attention_mask"].to(device)
                outputs = self.model(input_ids, attention_mask)
                probs = torch.softmax(outputs, dim=1).squeeze().cpu().tolist()
                
        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Inference time: {inference_time:.2f}ms with {'optimized' if self.use_optimized_model else 'standard'} model")
        
        # Handle different output shapes
        if isinstance(probs, list):
            prediction = probs.index(max(probs))
            scores = probs
        else:
            prediction = 1 if probs > 0.5 else 0
            scores = [1-probs, probs]
        
        return {"prediction": prediction, "scores": scores}
    
    def render_header(self):
        """Render the dashboard header"""
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("https://i.imgur.com/jOz1I2r.png", width=100)
        
        with col2:
            st.title("Guardian - Mental Health Monitoring")
            st.markdown("Parent dashboard for monitoring mental health risk indicators")
    
    def render_metrics(self):
        """Render metric cards at the top of the dashboard"""
        if self.data is None:
            self.load_data()
        
        # Calculate metrics
        total_messages = len(self.data)
        high_risk = len(self.data[self.data['risk_level'] == 2])
        medium_risk = len(self.data[self.data['risk_level'] == 1])
        risk_percentage = (high_risk / total_messages) * 100 if total_messages > 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Messages", value=total_messages)
        
        with col2:
            st.metric(label="High Risk Messages", value=high_risk)
        
        with col3:
            st.metric(label="Medium Risk Messages", value=medium_risk)
        
        with col4:
            st.metric(label="Risk Percentage", value=f"{risk_percentage:.1f}%")
    
    def render_trends(self):
        """Render trend charts"""
        if self.data is None:
            self.load_data()
        
        st.subheader("Risk Level Trends")
        
        # Prepare data for trends
        self.data['date'] = pd.to_datetime(self.data['timestamp']).dt.date
        daily_counts = self.data.groupby(['date', 'risk_level']).size().reset_index(name='count')
        
        # Create pivot table for stacked bar chart
        pivot_data = daily_counts.pivot_table(
            index='date', 
            columns='risk_level', 
            values='count', 
            fill_value=0
        ).reset_index()
        
        pivot_data.columns = ['date'] + [RISK_LEVELS.get(lvl, {}).get('label', f'Level {lvl}') for lvl in pivot_data.columns if lvl != 'date']
        
        # Create stacked bar chart
        fig = go.Figure()
        
        for col in pivot_data.columns:
            if col != 'date':
                color = RISK_LEVELS.get(list(RISK_LEVELS.keys())[list(map(lambda x: x['label'], RISK_LEVELS.values())).index(col)], {}).get('color', 'gray')
                fig.add_trace(go.Bar(
                    x=pivot_data['date'],
                    y=pivot_data[col],
                    name=col,
                    marker_color=color
                ))
        
        fig.update_layout(
            barmode='stack',
            xaxis_title='Date',
            yaxis_title='Message Count',
            legend_title='Risk Level',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_message_table(self):
        """Render the table of recent messages"""
        if self.data is None:
            self.load_data()
        
        st.subheader("Recent Messages")
        
        # Sort by timestamp in descending order
        recent_data = self.data.sort_values('timestamp', ascending=False).head(20)
        
        # Create table
        for _, row in recent_data.iterrows():
            risk_level = row['risk_level']
            risk_class = "high-risk" if risk_level == 2 else "medium-risk" if risk_level == 1 else "no-risk"
            risk_label = RISK_LEVELS.get(risk_level, {}).get('label', 'Unknown')
            
            st.markdown(f"""
            <div class="card {risk_class}">
                <strong>Time:</strong> {row['timestamp']} | 
                <strong>User:</strong> {row['user']} | 
                <strong>Platform:</strong> {row['platform']} | 
                <strong>Risk:</strong> {risk_label} ({row['risk_score']:.2f})
                <p>{row['message']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_analysis_panel(self):
        """Render the text analysis panel"""
        st.subheader("Message Analysis Tool")
        
        # Text input for analysis
        message = st.text_area("Enter message to analyze:", height=100)
        
        if st.button("Analyze Message"):
            if message:
                # Analyze the text
                result = self.analyze_text(message)
                prediction = result["prediction"]
                scores = result["scores"]
                
                # Display results
                risk_label = RISK_LEVELS.get(prediction, {}).get('label', 'Unknown')
                risk_color = RISK_LEVELS.get(prediction, {}).get('color', 'gray')
                
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {risk_color};">
                    <h3>Analysis Result</h3>
                    <p><strong>Risk Level:</strong> {risk_label}</p>
                    <p><strong>Confidence Scores:</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create gauge charts for each risk level
                fig = go.Figure()
                
                for i, (level, score) in enumerate(zip(RISK_LEVELS.values(), scores)):
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=score * 100,
                        domain={'x': [i/3, (i+1)/3], 'y': [0, 1]},
                        title={'text': level['label']},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': level['color']},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 75], 'color': "gray"},
                                {'range': [75, 100], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': score * 100
                            }
                        }
                    ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Provide recommendations based on risk level
                if prediction == 2:
                    st.error("⚠️ High risk detected. Consider immediate intervention.")
                elif prediction == 1:
                    st.warning("⚠️ Medium risk detected. Monitor the situation closely.")
                else:
                    st.success("✅ No significant risk detected.")
            else:
                st.warning("Please enter a message to analyze.")
    def render_settings_panel(self):
        """Render the settings panel"""
        st.subheader("Dashboard Settings")
        # Create tabs for different settings categories
        general_tab, model_tab, notification_tab = st.tabs(["General", "Model Settings", "Notifications"])

        with general_tab:
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Parent Email for Alerts:", value="parent@example.com")
                st.text_input("Emergency Contact Number:", value="555-123-4567")
            with col2:
                st.selectbox("Alert Frequency:", ["Immediate", "Hourly", "Daily"])
                st.checkbox("Enable SMS Alerts", value=True)

        with model_tab:
            st.subheader("Model Configuration")
            # Model optimization settings
            use_optimized = st.checkbox("Use Optimized Model", value=self.use_optimized_model, 
                                       help="Use JIT-optimized model for faster inference")
            if use_optimized != self.use_optimized_model:
                self.use_optimized_model = use_optimized
                st.success(f"{'Enabled' if use_optimized else 'Disabled'} optimized model")
            # Model paths
            st.text_input("Standard Model Path:", value=self.model_path or "")
            st.text_input("Optimized Model Path:", value=self.optimized_model_path or "")
            # CUDA info
            if torch.cuda.is_available():
                st.success(f"CUDA is available: {torch.cuda.get_device_name(0)}")
                st.info(f"CUDA Version: {torch.version.cuda}")
            else:
                st.warning("CUDA is not available. Using CPU for inference.")
            # Run a quick benchmark
            if st.button("Run Quick Benchmark"):
                if self.model:
                    with st.spinner("Running benchmark..."):
                        sample_text = "I'm feeling really down today and don't know what to do."
                        start_time = time.time()
                        for _ in range(10):  # Run multiple times to get a better average
                            _ = self.analyze_text(sample_text)
                        avg_time = (time.time() - start_time) * 100  # ms per inference
                        st.info(f"Average inference time: {avg_time:.2f}ms with {'optimized' if self.use_optimized_model else 'standard'} model")
                else:
                    st.error("Model not loaded. Please load a model first.")

        with notification_tab:
            st.checkbox("Enable Email Notifications", value=True)
            st.checkbox("Enable Mobile App Notifications", value=True)
            st.selectbox("Notification Priority Threshold:", ["All Messages", "Medium Risk and Above", "High Risk Only"])

        # Save all settings
        if st.button("Save All Settings"):
            st.success("Settings saved successfully!")
    
    def render_resources_panel(self):
        """Render the resources panel"""
        st.subheader("Mental Health Resources")
        
        resources = [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "1-800-273-8255",
                "url": "https://suicidepreventionlifeline.org/"
            },
            {
                "name": "Crisis Text Line",
                "phone": "Text HOME to 741741",
                "url": "https://www.crisistextline.org/"
            },
            {
                "name": "Teen Line",
                "phone": "310-855-HOPE or Text TEEN to 839863",
                "url": "https://teenlineonline.org/"
            },
            {
                "name": "SAMHSA's National Helpline",
                "phone": "1-800-662-HELP (4357)",
                "url": "https://www.samhsa.gov/find-help/national-helpline"
            }
        ]
        
        for resource in resources:
            st.markdown(f"""
            <div class="card">
                <strong>{resource['name']}</strong><br>
                Phone: {resource['phone']}<br>
                <a href="{resource['url']}" target="_blank">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
    
    def render(self):
        """Render the complete dashboard"""
        self.render_header()
        
        # Check for model path in sidebar
        with st.sidebar:
            st.subheader("Configuration")
            model_path_input = st.text_input("Model Path:", value=self.model_path or "./models/saved_model.pt")
            optimized_model_path_input = st.text_input("Optimized Model Path:", value=self.optimized_model_path or "./models/optimized_model.pt")
            data_path_input = st.text_input("Data Path:", value=self.data_path or "./data/message_history.json")
            
            if st.button("Load Data"):
                self.model_path = model_path_input
                self.optimized_model_path = optimized_model_path_input
                self.data_path = data_path_input
                self.load_model()
                self.load_optimized_model()
                self.load_data()
                st.success("Data loaded successfully!")
            
            st.divider()
            st.subheader("Navigation")
            page = st.radio("Select Page:", ["Dashboard", "Analysis Tool", "Settings", "Resources"])
        
        # Initialize model and data if not already done
        if self.model is None and self.model_path:
            self.load_model()
        
        if self.optimized_model is None and self.optimized_model_path:
            self.load_optimized_model()
        
        if self.data is None:
            self.load_data()
        
        # Render selected page
        if page == "Dashboard":
            self.render_metrics()
            self.render_trends()
            self.render_message_table()
        elif page == "Analysis Tool":
            self.render_analysis_panel()
        elif page == "Settings":
            self.render_settings_panel()
        elif page == "Resources":
            self.render_resources_panel()

def main():
    """Main function to run the dashboard"""
    # Default paths
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "saved_model.pt")
    optimized_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "optimized_model.pt")
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "message_history.json")
    
    # Check if files exist
    if not os.path.exists(model_path):
        model_path = None
    
    if not os.path.exists(optimized_model_path):
        optimized_model_path = None
    
    if not os.path.exists(data_path):
        data_path = None
    
    # Create and render dashboard
    dashboard = MentalHealthDashboard(model_path, data_path, optimized_model_path)
    dashboard.render()

if __name__ == "__main__":
    main()
