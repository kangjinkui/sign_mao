FROM mcr.microsoft.com/playwright:v1.58.2-jammy

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend /app

EXPOSE 5173
CMD ["npm", "run", "dev"]
