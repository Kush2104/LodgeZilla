FROM node:20-alpine AS frontend

# Set the working directory to /app
WORKDIR /myapp

# Copy package.json and package-lock.json to the container at /app
COPY package*.json /myapp

# Install app dependencies
RUN npm install --force

# Copy the current directory contents into the container at /app
COPY . .

# Build the React app
#RUN npm run build

# Make port 80 available to the world outside this container
EXPOSE 3000

# Serve the built frontend application
CMD ["npm", "start"]