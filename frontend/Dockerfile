# Imagen base: Node 18-alpine
FROM node:18-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer puerto 5173 (Vite)
EXPOSE 5173

# Comando para ejecutar el servidor de desarrollo con acceso desde fuera
CMD ["npm", "run", "dev", "--", "--host"]
