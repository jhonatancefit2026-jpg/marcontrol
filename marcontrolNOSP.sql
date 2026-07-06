CREATE DATABASE  marcontrol;
USE marcontrol;
CREATE TABLE especies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  nombre_cientifico VARCHAR(150),
  descripcion TEXT,
  UNIQUE (nombre)
);

CREATE TABLE embarcaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  matricula VARCHAR(30) NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  tipo ENUM('arrastrero','cerquero','palangrero','otro') ,
  ano_construccion YEAR,
  material_casco VARCHAR(50),
  eslora DECIMAL(6,2),
  manga DECIMAL(6,2),
  calado DECIMAL(6,2),
  capacidad_bodega_tn DECIMAL(8,2),
  potencia_motor_kw INT,
  velocidad_max_kn DECIMAL(5,2),
  autonomia_dias INT,
  equipos_navegacion TEXT,
  fecha_ultima_inspeccion DATE,
  estado ENUM('operativa','mantenimiento','baja')
);


CREATE TABLE licencias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero_licencia VARCHAR(50) NOT NULL UNIQUE,
  embarcacion_id INT NOT NULL,
  tipo_licencia VARCHAR(50),
  fecha_emision DATE,
  fecha_vencimiento DATE,
  autoridad_emisora VARCHAR(100),
  zonas_permitidas TEXT,
  cuotas_asignadas TEXT,
  FOREIGN KEY (embarcacion_id) REFERENCES embarcaciones(id) ON DELETE CASCADE
);

CREATE TABLE licencia_especies (
  licencia_id INT,
  especie_id INT,
  PRIMARY KEY (licencia_id, especie_id),
  FOREIGN KEY (licencia_id) REFERENCES licencias(id) ON DELETE CASCADE,
  FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE RESTRICT
);

CREATE TABLE zonas_pesca (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(30) NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  coordenadas VARCHAR(200),
  profundidad_promedio_m DECIMAL(6,2),
  temperatura_superficial_c DECIMAL(5,2),
  corrientes_predominantes VARCHAR(200),
  especies_habituales TEXT,
  restricciones TEXT
);

CREATE TABLE temporadas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  fecha_inicio DATE,
  fecha_fin DATE,
  especies_permitidas TEXT,
  cuotas_globales TEXT,
  metodos_autorizados TEXT
);

CREATE TABLE cuotas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  temporada_id INT NOT NULL,
  especie_id INT NOT NULL,
  cuota_kg DECIMAL(12,2) NOT NULL,
  cuota_restante_kg DECIMAL(12,2) NOT NULL,
  UNIQUE (temporada_id, especie_id),
  FOREIGN KEY (temporada_id) REFERENCES temporadas(id) ON DELETE CASCADE,
  FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE RESTRICT
);

CREATE TABLE tripulantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dni VARCHAR(30) NOT NULL UNIQUE,
  nombres VARCHAR(100),
  apellidos VARCHAR(100),
  fecha_nacimiento DATE,
  direccion VARCHAR(200),
  telefono VARCHAR(50),
  libreta_embarque VARCHAR(50),
  cargo VARCHAR(80),
  experiencia_anios INT,
  estado_salud VARCHAR(100),
  disponible BOOLEAN
);

CREATE TABLE certificados (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(200)
);

CREATE TABLE tripulante_certificados (
  tripulante_id INT,
  certificado_id INT,
  fecha_emision DATE,
  fecha_vencimiento DATE,
  PRIMARY KEY (tripulante_id, certificado_id),
  FOREIGN KEY (tripulante_id) REFERENCES tripulantes(id) ON DELETE CASCADE,
  FOREIGN KEY (certificado_id) REFERENCES certificados(id) ON DELETE RESTRICT
);

CREATE TABLE equipos_pesca (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  tipo ENUM('red','anzuelos','trampa','otros'),
  caracteristicas TEXT,
  fecha_adquisicion DATE,
  costo DECIMAL(12,2),
  vida_util_anios INT,
  embarcacion_id INT,
  FOREIGN KEY (embarcacion_id) REFERENCES embarcaciones(id) ON DELETE SET NULL
);

CREATE TABLE mantenimientos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  equipo_id INT,
  embarcacion_id INT,
  fecha DATE,
  tipo_mantenimiento VARCHAR(80),
  descripcion TEXT,
  repuestos_utilizados TEXT,
  costo DECIMAL(12,2),
  responsable VARCHAR(100),
  FOREIGN KEY (equipo_id) REFERENCES equipos_pesca(id) ON DELETE SET NULL,
  FOREIGN KEY (embarcacion_id) REFERENCES embarcaciones(id) ON DELETE CASCADE
);

CREATE TABLE capturas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero_registro VARCHAR(60) NOT NULL UNIQUE,
  embarcacion_id INT NOT NULL,
  zona_id INT NOT NULL,
  fecha_inicio DATETIME,
  fecha_fin DATETIME,
  metodo_pesca VARCHAR(80),
  condiciones_climaticas VARCHAR(200),
  FOREIGN KEY (embarcacion_id) REFERENCES embarcaciones(id) ON DELETE CASCADE,
  FOREIGN KEY (zona_id) REFERENCES zonas_pesca(id) ON DELETE RESTRICT
);

CREATE TABLE captura_detalle (
  captura_id INT,
  especie_id INT,
  cantidad_kg DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (captura_id, especie_id),
  FOREIGN KEY (captura_id) REFERENCES capturas(id) ON DELETE CASCADE,
  FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE RESTRICT
);

CREATE TABLE procesamiento (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lote_codigo VARCHAR(60) NOT NULL UNIQUE,
  captura_id INT,
  fecha DATE,
  especie_id INT,
  materia_prima_kg DECIMAL(12,2),
  metodo_procesamiento ENUM('congelado','enlatado','salado','otro'),
  rendimiento DECIMAL(6,2),
  tipo_producto_final VARCHAR(100),
  cantidad_producida_kg DECIMAL(12,2),
  responsable VARCHAR(100),
  FOREIGN KEY (captura_id) REFERENCES capturas(id) ON DELETE SET NULL,
  FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE RESTRICT
);

CREATE TABLE control_calidad (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lote_codigo VARCHAR(60),
  fecha DATE,
  parametros_analizados TEXT,
  resultados TEXT,
  cumple_standards BOOLEAN,
  inspector VARCHAR(100),
  decision ENUM('aprobado','rechazado','cuarentena'),
  FOREIGN KEY (lote_codigo) REFERENCES procesamiento(lote_codigo) ON DELETE SET NULL
);

CREATE TABLE productos_procesados (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo_producto VARCHAR(80) NOT NULL UNIQUE,
  descripcion VARCHAR(200),
  tipo_procesamiento VARCHAR(80),
  presentacion VARCHAR(80),
  empaque VARCHAR(80),
  peso_neto_g DECIMAL(8,2),
  fecha_produccion DATE,
  fecha_vencimiento DATE,
  temp_conservacion_c DECIMAL(5,2),
  precio DECIMAL(12,2),
  lote_codigo VARCHAR(60),
  FOREIGN KEY (lote_codigo) REFERENCES procesamiento(lote_codigo) ON DELETE SET NULL
);

CREATE TABLE asignaciones_tripulantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tripulante_id INT NOT NULL,
  embarcacion_id INT NOT NULL,
  fecha_inicio DATE,
  fecha_fin DATE,
  cargo_a_bordo VARCHAR(80),
  FOREIGN KEY (tripulante_id) REFERENCES tripulantes(id) ON DELETE CASCADE,
  FOREIGN KEY (embarcacion_id) REFERENCES embarcaciones(id) ON DELETE CASCADE
);


INSERT INTO especies (nombre, nombre_cientifico, descripcion) VALUES
('Atún','Thunnus albacares','Atún de alta demanda'),
('Merluza','Merluccius hubbsi','Pez blanco común'),
('Salmón','Salmo salar','Salmón atlántico'),
('Sardina','Sardinops sagax','Pequeña pelágica'),
('Bacalao','Gadus morhua','Fondo marino'),
('Calamar','Loligo vulgaris','Cephalópodo'),
('Lenguado','Solea solea','Pez plano'),
('Caballa','Scomber scombrus','Pelágico migratorio'),
('Camarón','Penaeus vannamei','Crustáceo'),
('Pargo','Lutjanus spp.','Demanda local'),
('Corvina','Cilus gilberti','Especie costera'),
('Raya','Dasyatis pastinaca','Cartilaginoso');

-- 2) embarcaciones (12)
INSERT INTO embarcaciones (matricula, nombre, tipo, ano_construccion, material_casco, eslora, manga, calado, capacidad_bodega_tn, potencia_motor_kw, velocidad_max_kn, autonomia_dias, equipos_navegacion, fecha_ultima_inspeccion, estado) VALUES
('MAT-001','Marinero I','arrastrero',2005,'Acero',45.00,8.50,4.60,120.00,1500,14.5,20,'Radar, GPS', '2025-06-10', 'operativa'),
('MAT-002','Océano Rey','cerquero',2010,'Fibra',38.50,7.20,3.80,80.00,900,12.0,15,'GPS, Eco-sonar','2025-03-15','operativa'),
('MAT-003','Neptuno','palangrero',2012,'Acero',50.00,9.00,5.00,150.00,1800,15.2,25,'Radar, AIS','2024-11-02','operativa'),
('MAT-004','Brisa','cerquero',2018,'Aluminio',30.00,6.50,3.20,45.00,650,11.5,10,'GPS','2025-01-20','operativa'),
('MAT-005','Aurora','arrastrero',2000,'Acero',48.00,8.80,4.90,140.00,1600,13.5,30,'Radar','2024-12-01','mantenimiento'),
('MAT-006','Tridente','palangrero',2015,'Acero',46.00,8.00,4.50,110.00,1400,13.0,18,'GPS, Radar','2025-08-12','operativa'),
('MAT-007','Viento','otro',2008,'Fibra',22.00,5.00,2.50,20.00,300,10.0,7,'GPS','2025-07-18','operativa'),
('MAT-008','Sirena','cerquero',2011,'Acero',33.00,6.80,3.40,60.00,700,11.8,12,'Eco-sonar','2025-05-05','operativa'),
('MAT-009','Albatros','arrastrero',1999,'Acero',55.00,10.00,5.50,200.00,2000,16.0,40,'Radar, GPS, AIS','2025-09-09','operativa'),
('MAT-010','Pacifico','palangrero',2003,'Acero',42.00,7.80,4.00,95.00,1200,12.5,16,'GPS, AIS','2025-02-02','operativa'),
('MAT-011','Costa Linda','cerquero',2019,'Aluminio',28.00,6.00,3.00,35.00,500,10.5,8,'GPS','2025-04-01','operativa'),
('MAT-012','Fuego Marino','otro',2016,'Fibra',18.00,4.50,2.20,12.00,200,9.0,5,'GPS','2025-08-01','operativa');

-- 3) licencias (12)
INSERT INTO licencias (numero_licencia, embarcacion_id, tipo_licencia, fecha_emision, fecha_vencimiento, autoridad_emisora, zonas_permitidas, cuotas_asignadas) VALUES
('LIC-2024-001',1,'Comercial','2024-01-01','2026-01-01','Autoridad Marina','Z1,Z2','Atún:5000'),
('LIC-2024-002',2,'Artesanal','2023-06-15','2025-06-15','Autoridad Regional','Z3','Merluza:2000'),
('LIC-2024-003',3,'Comercial','2024-03-10','2025-03-09','Autoridad Marina','Z1,Z4','Salmón:1000'),
('LIC-2024-004',4,'Artesanal','2024-02-01','2025-02-01','Autoridad Local','Z2','Sardina:1500'),
('LIC-2024-005',5,'Comercial','2022-09-01','2024-09-01','Autoridad Marina','Z1,Z2','Bacalao:800'),
('LIC-2024-006',6,'Comercial','2024-05-05','2026-05-05','Autoridad Marina','Z4','Calamar:2000'),
('LIC-2024-007',7,'Recreativa','2024-07-01','2025-07-01','Autoridad Local','Z5',''),
('LIC-2024-008',8,'Artesanal','2023-11-11','2024-11-11','Autoridad Regional','Z3,Z6','Caballa:1000'),
('LIC-2024-009',9,'Comercial','2024-08-08','2026-08-08','Autoridad Marina','Z1,Z2,Z4','Atún:8000'),
('LIC-2024-010',10,'Comercial','2022-04-04','2024-04-04','Autoridad Marina','Z4','Pargo:500'),
('LIC-2024-011',11,'Artesanal','2024-02-20','2025-02-20','Autoridad Local','Z6','Corvina:300'),
('LIC-2024-012',12,'Recreativa','2024-06-06','2025-06-06','Autoridad Local','Z5','');

-- 4) licencia_especies (vincular licencias ↔ especies) -- 12 relaciones variadas
INSERT INTO licencia_especies (licencia_id, especie_id) VALUES
(1,1),(1,8),(2,2),(3,3),(4,4),(5,5),(6,6),(8,8),(9,1),(9,8),(10,10),(11,11);

-- 5) zonas_pesca (12)
INSERT INTO zonas_pesca (codigo, nombre, coordenadas, profundidad_promedio_m, temperatura_superficial_c, corrientes_predominantes, especies_habituales, restricciones) VALUES
('Z1','Banco Norte','-12.45,-77.03',200.00,14.5,'Corriente fría','Atún;Caballa;Calamar','veda parcial'),
('Z2','Costa Sur','-13.00,-76.50',80.00,16.0,'Corriente templada','Merluza;Pargo','reserva marina'),
('Z3','Golfo Este','-11.90,-76.00',60.00,18.2,'Corriente cálida','Sardina;Corvina','ninguna'),
('Z4','Estrecho Central','-12.80,-77.50',300.00,12.8,'Corriente fría y profunda','Atún;Bacalao','vigilancia'),
('Z5','Islas Menores','-12.00,-76.20',25.00,20.0,'corriente cálida','Camarón;Corvina','temporalmente cerrada'),
('Z6','Playa Norte','-12.20,-77.30',40.00,17.5,'alta productividad','Caballa;Sardina','ninguna'),
('Z7','Banco Sur','-13.50,-76.90',220.00,13.5,'corriente fría','Lenguado;Raya','veda'),
('Z8','Archipiélago','-12.75,-77.10',50.00,19.0,'corriente cálida','Pargo;Corvina','zonas protegidas'),
('Z9','Canal Oeste','-12.90,-77.40',100.00,15.0,'corriente variable','Merluza;Calamar','ninguna'),
('Z10','Banco Interior','-13.10,-76.60',150.00,14.0,'corriente fría','Atún;Bacalao','restricción por tallas'),
('Z11','Bahía Este','-12.60,-77.20',30.00,18.8,'alta productividad','Sardina;Camarón','ninguna'),
('Z12','Plataforma Lejana','-13.90,-76.20',400.00,11.5,'corriente fría profunda','Bacalao;Atún','cierre temporal');

-- 6) temporadas (12)
INSERT INTO temporadas (nombre, fecha_inicio, fecha_fin, especies_permitidas, cuotas_globales, metodos_autorizados) VALUES
('Temporada 2024-1','2024-01-01','2024-06-30','Atún,Merluza,Salmón','Atún:10000,Merluza:5000','arrastre,palangre,cerco'),
('Temporada 2024-2','2024-07-01','2024-12-31','Sardina,Camarón','Sardina:8000,Camarón:2000','cerco,artesanal'),
('Temporada 2023-1','2023-01-01','2023-06-30','Bacalao,Calamar','Bacalao:3000,Calamar:4000','palangre,arrastre'),
('Temporada 2025-1','2025-01-01','2025-06-30','Atún,Calamar','Atún:12000,Calamar:5000','arrastre,palangre'),
('Temporada 2024-3','2024-09-01','2024-11-30','Pargo,Corvina','Pargo:1000,Corvina:800','artesanal'),
('Temporada 2024-4','2024-02-01','2024-02-28','Merluza','Merluza:2000','artesanal'),
('Temporada 2024-5','2024-03-01','2024-05-31','Salmón','Salmón:1200','palangre'),
('Temporada 2024-6','2024-10-01','2024-12-31','Lenguado,Raya','Lenguado:500,Raya:300','artesanal'),
('Temporada 2023-2','2023-07-01','2023-12-31','Caballa,Sardina','Caballa:6000,Sardina:7000','cerco'),
('Temporada 2024-7','2024-06-01','2024-06-30','Atún','Atún:2000','palangre'),
('Temporada 2022-1','2022-01-01','2022-12-31','Varios','Varios','varios'),
('Temporada 2024-8','2024-04-01','2024-04-30','Camarón','Camarón:1500','artesanal');

-- 7) cuotas (12) -> asociadas a temporadas y especies
INSERT INTO cuotas (temporada_id, especie_id, cuota_kg, cuota_restante_kg) VALUES
(1,1,10000,10000),(1,2,5000,5000),(2,4,8000,8000),(3,5,3000,3000),
(4,1,12000,12000),(5,10,1000,1000),(6,2,2000,2000),(7,3,1200,1200),
(8,7,500,500),(9,8,6000,6000),(2,9,2000,2000),(11,1,3000,3000);

-- 8) tripulantes (12)
INSERT INTO tripulantes (dni, nombres, apellidos, fecha_nacimiento, direccion, telefono, libreta_embarque, cargo, experiencia_anios, estado_salud, disponible) VALUES
('DNI001','Carlos','Perez','1980-05-12','Av. Mar 123','+57-300111222','LB-001','Capitán',20,'Bueno',TRUE),
('DNI002','Ana','Gomez','1985-07-20','Calle 5','+57-300222333','LB-002','Primer Oficial',12,'Bueno',TRUE),
('DNI003','Juan','Rodriguez','1978-03-01','Barrio Azul','+57-300333444','LB-003','Jefe de Máquinas',18,'Bueno',TRUE),
('DNI004','Miguel','Lopez','1990-10-10','Puerto Viejo','+57-300444555','LB-004','Marinero',5,'Bueno',TRUE),
('DNI005','Luisa','Martinez','1992-12-12','Costa 9','+57-300555666','LB-005','Marinero',3,'Bueno',TRUE),
('DNI006','Pedro','Sanchez','1975-06-06','Col. Marina','+57-300666777','LB-006','Capitán',25,'Bueno',TRUE),
('DNI007','Sofia','Diaz','1988-01-01','Villa Norte','+57-300777888','LB-007','Cocinero',8,'Bueno',TRUE),
('DNI008','Andres','Ruiz','1993-09-09','Sector 7','+57-300888999','LB-008','Primer Oficial',6,'Bueno',TRUE),
('DNI009','Raul','Torres','1982-02-02','Pueblo','+57-300999000','LB-009','Jefe de Máquinas',14,'Bueno',TRUE),
('DNI010','María','Lozano','1995-11-11','Isla','+57-300101010','LB-010','Marinera',2,'Bueno',TRUE),
('DNI011','Diego','Ramos','1987-04-04','Puerto Nuevo','+57-300111333','LB-011','Marinero',7,'Bueno',TRUE),
('DNI012','Elena','Vargas','1991-08-08','Bajada','+57-300222444','LB-012','Capitán',10,'Bueno',TRUE);

-- 9) certificados (12)
INSERT INTO certificados (codigo, descripcion) VALUES
('CERT-001','Capacitacion Básica de Seguridad'),
('CERT-002','Patrón de Embarcación'),
('CERT-003','Mecánica Marina'),
('CERT-004','Manipulación de Alimentos'),
('CERT-005','Primeros Auxilios'),
('CERT-006','Tripulación Avanzada'),
('CERT-007','Certificado Radar'),
('CERT-008','Certificado AIS'),
('CERT-009','Certificado Buceo'),
('CERT-010','Certificado Conservación'),
('CERT-011','Licencia de Radio'),
('CERT-012','Formación Ambiental');

-- 10) tripulante_certificados (12 relaciones)
INSERT INTO tripulante_certificados (tripulante_id, certificado_id, fecha_emision, fecha_vencimiento) VALUES
(1,1,'2018-01-01','2028-01-01'),
(1,2,'2015-03-01','2025-03-01'),
(2,1,'2019-01-01','2029-01-01'),
(2,7,'2020-06-06','2026-06-06'),
(3,3,'2017-05-05','2027-05-05'),
(4,1,'2021-01-01','2031-01-01'),
(5,4,'2022-02-02','2027-02-02'),
(6,2,'2005-05-05','2030-05-05'),
(7,4,'2020-11-11','2025-11-11'),
(8,2,'2021-10-10','2026-10-10'),
(9,3,'2016-04-04','2026-04-04'),
(12,2,'2019-07-07','2029-07-07');

-- 11) equipos_pesca (12)
INSERT INTO equipos_pesca (codigo, tipo, caracteristicas, fecha_adquisicion, costo, vida_util_anios, embarcacion_id) VALUES
('EQ-001','red','Red arrastre 200m','2015-01-01',50000,10,1),
('EQ-002','anzuelos','Línea de palangre 1000 anzuelos','2018-06-06',20000,8,3),
('EQ-003','trampa','Trampas para crustáceos','2019-03-03',8000,6,2),
('EQ-004','red','Red de cerco 150m','2020-07-07',30000,7,2),
('EQ-005','anzuelos','Palangre pequeño','2017-09-09',12000,8,6),
('EQ-006','trampa','Trampa experimental','2021-02-02',5000,5,NULL),
('EQ-007','red','Red auxiliar','2016-12-12',10000,6,5),
('EQ-008','anzuelos','Anzuelos especiales','2022-05-05',7000,5,10),
('EQ-009','otros','Sonda profunda','2014-04-04',15000,12,9),
('EQ-010','red','Red de repuesto','2013-08-08',9000,9,11),
('EQ-011','trampa','Trampas costeras','2018-10-10',6000,6,8),
('EQ-012','otros','Equipo de AIS','2020-01-01',4000,10,4);

-- 12) mantenimientos (12)
INSERT INTO mantenimientos (equipo_id, embarcacion_id, fecha, tipo_mantenimiento, descripcion, repuestos_utilizados, costo, responsable) VALUES
(1,1,'2025-07-01','Preventivo','Cambio de cables','cables','1500','Taller Mar'),
(2,3,'2025-06-15','Correctivo','Reparación motores','motores','5000','Mecánico S.A.'),
(3,2,'2025-04-10','Preventivo','Revisión trampas','mallas','300','Tecnico Local'),
(4,2,'2025-05-05','Preventivo','Inspección red cerco',NULL,200,'Taller Mar'),
(5,6,'2025-03-12','Correctivo','Cambio anzuelos',NULL,150,'Mecánico S.A.'),
(6,NULL,'2025-01-20','Preventivo','Ajustes trapas','mallas',100,'Taller Mar'),
(7,5,'2024-12-01','Correctivo','Reparación cabos','cabos',400,'Taller Mar'),
(8,10,'2025-02-02','Preventivo','Chequeo',NULL,80,'Tecnico Local'),
(9,9,'2025-09-09','Instrumental','Calibración sonda',NULL,600,'Proveedor X'),
(10,11,'2025-04-14','Preventivo','Cambio mallas',NULL,250,'Taller Mar'),
(11,8,'2025-05-21','Correctivo','Reemplazo piezas',NULL,350,'Mecánico S.A.'),
(12,4,'2025-08-01','Preventivo','Actualización AIS',NULL,200,'Proveedor X');

-- 13) capturas (12)
INSERT INTO capturas (numero_registro, embarcacion_id, zona_id, fecha_inicio, fecha_fin, metodo_pesca, condiciones_climaticas) VALUES
('CAP-20240201-01',1,1,'2024-02-01 06:00:00','2024-02-01 18:00:00','arrastre','viento 5 nudos'),
('CAP-20240205-01',2,3,'2024-02-05 04:00:00','2024-02-05 14:00:00','cerco','mar calma'),
('CAP-20240210-01',3,4,'2024-02-10 05:00:00','2024-02-10 20:00:00','palangre','bruma ligera'),
('CAP-20240215-01',4,2,'2024-02-15 07:00:00','2024-02-15 15:00:00','cerco','corriente moderada'),
('CAP-20240220-01',5,1,'2024-02-20 06:30:00','2024-02-20 19:00:00','arrastre','mar agitado'),
('CAP-20240225-01',6,4,'2024-02-25 05:30:00','2024-02-25 18:30:00','palangre','viento fuerte'),
('CAP-20240301-01',7,5,'2024-03-01 06:00:00','2024-03-01 16:00:00','artesanal','buen tiempo'),
('CAP-20240305-01',8,6,'2024-03-05 05:00:00','2024-03-05 13:00:00','cerco','mar calma'),
('CAP-20240401-01',9,1,'2024-04-01 06:00:00','2024-04-01 20:00:00','arrastre','brisa'),
('CAP-20240405-01',10,4,'2024-04-05 04:00:00','2024-04-05 18:00:00','palangre','nublado'),
('CAP-20240501-01',11,6,'2024-05-01 06:00:00','2024-05-01 12:00:00','cerco','mar calma'),
('CAP-20240505-01',12,5,'2024-05-05 05:00:00','2024-05-05 14:00:00','artesanal','bruma');

-- 14) captura_detalle (12) -> asignar especies a capturas
INSERT INTO captura_detalle (captura_id, especie_id, cantidad_kg) VALUES
(1,1,2000.00),(1,8,500.00),(2,4,800.00),(3,1,1200.00),(4,2,400.00),(5,5,600.00),
(6,6,900.00),(7,11,300.00),(8,8,1200.00),(9,1,5000.00),(10,10,200.00),(11,4,700.00);

-- 15) procesamiento (12)
INSERT INTO procesamiento (lote_codigo, captura_id, fecha, especie_id, materia_prima_kg, metodo_procesamiento, rendimiento, tipo_producto_final, cantidad_producida_kg, responsable) VALUES
('LOT-0001',1,'2024-02-02',1,1500,'congelado',60.00,'Atún en filete',900,'Jefe Planta'),
('LOT-0002',2,'2024-02-06',4,700,'enlatado',55.00,'Sardina en lata',385,'Jefe Planta'),
('LOT-0003',3,'2024-02-11',1,1000,'congelado',58.00,'Atún filete',580,'Jefe Planta'),
('LOT-0004',4,'2024-02-16',2,350,'congelado',62.00,'Merluza filete',217,'Jefe Planta'),
('LOT-0005',5,'2024-02-21',5,500,'salado',45.00,'Bacalao salado',225,'Jefe Planta'),
('LOT-0006',6,'2024-02-26',6,800,'congelado',50.00,'Calamar entero',400,'Jefe Planta'),
('LOT-0007',7,'2024-03-02',11,250,'congelado',65.00,'Corvina filete',162.5,'Jefe Planta'),
('LOT-0008',8,'2024-03-06',8,1000,'congelado',60.00,'Caballa filete',600,'Jefe Planta'),
('LOT-0009',9,'2024-04-02',1,4000,'congelado',59.00,'Atún entero',2360,'Jefe Planta'),
('LOT-0010',10,'2024-04-06',10,180,'congelado',63.00,'Pargo filete',113.4,'Jefe Planta'),
('LOT-0011',11,'2024-05-02',4,600,'enlatado',54.00,'Sardina en lata',324,'Jefe Planta'),
('LOT-0012',12,'2024-05-06',9,120,'congelado',55.00,'Camarón congelado',66,'Jefe Planta');

-- 16) control_calidad (12) -- algunos aprobados/rechazados
INSERT INTO control_calidad (lote_codigo, fecha, parametros_analizados, resultados, cumple_standards, inspector, decision) VALUES
('LOT-0001','2024-02-03','temp, ph','OK',TRUE,'Inspector A','aprobado'),
('LOT-0002','2024-02-07','temp, sal','OK',TRUE,'Inspector B','aprobado'),
('LOT-0003','2024-02-12','temp','OK',TRUE,'Inspector C','aprobado'),
('LOT-0004','2024-02-17','microbiologia','nivel alto',FALSE,'Inspector D','rechazado'),
('LOT-0005','2024-02-22','rendimiento','bajo',FALSE,'Inspector E','cuarentena'),
('LOT-0006','2024-02-27','temp','OK',TRUE,'Inspector A','aprobado'),
('LOT-0007','2024-03-03','temp','OK',TRUE,'Inspector C','aprobado'),
('LOT-0008','2024-03-07','imagen','OK',TRUE,'Inspector B','aprobado'),
('LOT-0009','2024-04-03','temp','OK',TRUE,'Inspector A','aprobado'),
('LOT-0010','2024-04-07','ph','OK',TRUE,'Inspector D','aprobado'),
('LOT-0011','2024-05-03','sal','OK',TRUE,'Inspector B','aprobado'),
('LOT-0012','2024-05-07','temp','OK',TRUE,'Inspector A','aprobado');

-- 17) productos_procesados (12) -- algunos ya insertados por trigger pero insertamos ejemplo adicional
INSERT INTO productos_procesados (codigo_producto, descripcion, tipo_procesamiento, presentacion, empaque, peso_neto_g, fecha_produccion, fecha_vencimiento, temp_conservacion_c, precio, lote_codigo) VALUES
('PR-LOT1','Atún filete 1kg','congelado','filete','caja',1000,'2024-02-02','2025-02-02',-18,10,'LOT-0001'),
('PR-LOT2','Sardina lata 200g','enlatado','lata','pack',200,'2024-02-06','2026-02-06',5,1.5,'LOT-0002'),
('PR-LOT3','Atún filete 500g','congelado','filete','caja',500,'2024-02-11','2025-02-11',-18,6,'LOT-0003'),
('PR-LOT4','Merluza 1kg','congelado','filete','caja',1000,'2024-02-17','2025-02-17',-18,8,'LOT-0004'),
('PR-LOT5','Bacalao salado 1kg','salado','pieza','saco',1000,'2024-02-22','2025-02-22',10,9,'LOT-0005'),
('PR-LOT6','Calamar 1kg','congelado','entero','caja',1000,'2024-02-27','2025-02-27',-18,7,'LOT-0006'),
('PR-LOT7','Corvina 500g','congelado','filete','caja',500,'2024-03-03','2025-03-03',-18,5,'LOT-0007'),
('PR-LOT8','Caballa 1kg','congelado','filete','caja',1000,'2024-03-07','2025-03-07',-18,4,'LOT-0008'),
('PR-LOT9','Atún entero 10kg','congelado','entero','caja',10000,'2024-04-03','2025-04-03',-18,80,'LOT-0009'),
('PR-LOT10','Pargo 1kg','congelado','filete','caja',1000,'2024-04-07','2025-04-07',-18,6,'LOT-0010'),
('PR-LOT11','Sardina lata 400g','enlatado','lata','pack',400,'2024-05-03','2026-05-03',5,2.5,'LOT-0011'),
('PR-LOT12','Camarón 500g','congelado','bag','bolsa',500,'2024-05-07','2025-05-07',-18,6,'LOT-0012');

-- 18) asignaciones_tripulantes (12)
INSERT INTO asignaciones_tripulantes (tripulante_id, embarcacion_id, fecha_inicio, fecha_fin, cargo_a_bordo) VALUES
(1,1,'2024-01-01','2024-12-31','Capitán'),
(2,1,'2024-01-01','2024-12-31','Primer Oficial'),
(3,1,'2024-01-01','2024-12-31','Jefe de Máquinas'),
(4,2,'2024-02-01','2024-08-01','Marinero'),
(5,3,'2024-03-01',NULL,'Marinero'),
(6,9,'2024-01-01','2024-12-31','Capitán'),
(7,5,'2024-02-15','2024-09-15','Cocinero'),
(8,3,'2024-04-01','2024-10-01','Primer Oficial'),
(9,6,'2024-03-01','2024-12-01','Jefe de Máquinas'),
(10,11,'2024-05-01','2024-09-01','Marinera'),
(11,4,'2024-06-01',NULL,'Marinero'),
(12,12,'2024-07-01','2024-12-31','Capitán');
