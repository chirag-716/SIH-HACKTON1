import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  AccessTime,
  BookOnline,
  Dashboard,
  NotificationsActive,
  QueueMusic,
  Phone,
  Email,
  LocationOn,
  CheckCircle,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: <BookOnline color="primary" />,
      title: 'Online Booking',
      description: 'Book your appointment online from anywhere, anytime',
    },
    {
      icon: <AccessTime color="primary" />,
      title: 'Real-time Updates',
      description: 'Get live updates on queue status and waiting times',
    },
    {
      icon: <NotificationsActive color="primary" />,
      title: 'Smart Notifications',
      description: 'Receive SMS and email alerts about your appointment',
    },
    {
      icon: <Dashboard color="primary" />,
      title: 'Track Progress',
      description: 'Monitor your appointment status in real-time',
    },
  ];

  const services = [
    'New Electricity Connection',
    'Bill Payment and Queries',
    'Load Enhancement',
    'Meter Replacement',
    'Complaint Registration',
    'Subsidy Applications',
    'Name Transfer',
    'Disconnection/Reconnection',
  ];

  const offices = [
    {
      name: 'GUVNL Head Office',
      address: 'Sardar Patel Vidyut Bhavan, Race Course, Vadodara',
      phone: '+91-265-2355501',
      status: 'Open',
    },
    {
      name: 'GUVNL Ahmedabad Division',
      address: 'Urja Bhavan, Gandhinagar Road, Ahmedabad',
      phone: '+91-79-23254800',
      status: 'Open',
    },
    {
      name: 'GUVNL Surat Division',
      address: 'Vidyut Bhavan, VIP Road, Surat',
      phone: '+91-261-2463200',
      status: 'Open',
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 2 }}>
          GUVNL Queue Management System
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: 800, mx: 'auto' }}>
          Skip the long queues! Book your appointment online and get real-time updates 
          for all Gujarat Urja Vikas Nigam Limited (GUVNL) services.
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          {isAuthenticated ? (
            <>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/book-appointment')}
                startIcon={<BookOnline />}
                sx={{ px: 4, py: 1.5 }}
              >
                Book Appointment
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/my-appointments')}
                startIcon={<QueueMusic />}
                sx={{ px: 4, py: 1.5 }}
              >
                My Appointments
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/register')}
                sx={{ px: 4, py: 1.5 }}
              >
                Get Started
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/queue-status')}
                startIcon={<QueueMusic />}
                sx={{ px: 4, py: 1.5 }}
              >
                View Queue Status
              </Button>
            </>
          )}
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 6 }}>
        <Typography variant="h4" component="h2" textAlign="center" gutterBottom sx={{ mb: 4 }}>
          Why Choose Our System?
        </Typography>
        
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
                <CardContent>
                  <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h6" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Services Section */}
      <Box sx={{ py: 6 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Typography variant="h4" component="h2" gutterBottom>
              Available Services
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Book appointments for any of the following GUVNL services:
            </Typography>
            
            <List>
              {services.map((service, index) => (
                <ListItem key={index} sx={{ pl: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <CheckCircle color="primary" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={service} />
                </ListItem>
              ))}
            </List>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="h4" component="h2" gutterBottom>
              Office Locations
            </Typography>
            
            {offices.map((office, index) => (
              <Paper key={index} sx={{ p: 3, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h3">
                    {office.name}
                  </Typography>
                  <Chip
                    label={office.status}
                    color="success"
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LocationOn fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    {office.address}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Phone fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    {office.phone}
                  </Typography>
                </Box>
              </Paper>
            ))}
          </Grid>
        </Grid>
      </Box>

      {/* CTA Section */}
      {!isAuthenticated && (
        <Box sx={{ py: 6 }}>
          <Paper sx={{ p: 6, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h4" component="h2" gutterBottom>
              Ready to Get Started?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              Join thousands of citizens who have simplified their GUVNL experience
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/register')}
                sx={{ 
                  px: 4, 
                  py: 1.5, 
                  bgcolor: 'white', 
                  color: 'primary.main',
                  '&:hover': { bgcolor: 'grey.100' }
                }}
              >
                Create Account
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/login')}
                sx={{ 
                  px: 4, 
                  py: 1.5, 
                  borderColor: 'white', 
                  color: 'white',
                  '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                }}
              >
                Sign In
              </Button>
            </Box>
          </Paper>
        </Box>
      )}
    </Container>
  );
};

export default HomePage;