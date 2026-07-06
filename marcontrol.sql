-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1:3306
-- Tiempo de generación: 15-03-2026 a las 23:45:18
-- Versión del servidor: 9.1.0
-- Versión de PHP: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `marcontrol`
--

DELIMITER $$
--
-- Procedimientos
--
DROP PROCEDURE IF EXISTS `ActualizarCuotas`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ActualizarCuotas` (IN `p_especie_id` INT, IN `p_cantidad_kg` DECIMAL(10,2))   BEGIN
  UPDATE cuotas
  SET cuota_disponible = GREATEST(cuota_disponible - p_cantidad_kg, 0)
  WHERE especie_id = p_especie_id;
END$$

DROP PROCEDURE IF EXISTS `AsignarTripulantes`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `AsignarTripulantes` (IN `p_embarcacion_id` INT, IN `p_tripulante_id` INT)   BEGIN
  INSERT INTO embarcacion_tripulante(embarcacion_id, tripulante_id, fecha_asignacion)
  VALUES(p_embarcacion_id, p_tripulante_id, CURDATE());
END$$

DROP PROCEDURE IF EXISTS `ProcesarLotePescado`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ProcesarLotePescado` (IN `p_captura_id` INT, IN `p_rendimiento` DECIMAL(5,2), IN `p_calidad` VARCHAR(50))   BEGIN
  INSERT INTO procesamiento(captura_id, rendimiento, calidad, fecha_proceso)
  VALUES(p_captura_id, p_rendimiento, p_calidad, CURDATE());
END$$

DROP PROCEDURE IF EXISTS `ProgramarMantenimientoEmbarcacion`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ProgramarMantenimientoEmbarcacion` (IN `p_embarcacion_id` INT, IN `p_fecha` DATE, IN `p_descripcion` VARCHAR(255))   BEGIN
  INSERT INTO mantenimiento(embarcacion_id, fecha_mantenimiento, descripcion)
  VALUES(p_embarcacion_id, p_fecha, p_descripcion);
END$$

DROP PROCEDURE IF EXISTS `RegistrarCaptura`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `RegistrarCaptura` (IN `p_embarcacion_id` INT, IN `p_zona_id` INT, IN `p_fecha_inicio` DATE, IN `p_fecha_fin` DATE, IN `p_especie_id` INT, IN `p_cantidad_kg` DECIMAL(10,2))   BEGIN
  INSERT INTO capturas(embarcacion_id, zona_id, fecha_inicio, fecha_fin)
  VALUES(p_embarcacion_id, p_zona_id, p_fecha_inicio, p_fecha_fin);

  INSERT INTO captura_detalle(captura_id, especie_id, cantidad_kg)
  VALUES(LAST_INSERT_ID(), p_especie_id, p_cantidad_kg);
END$$

--
-- Funciones
--
DROP FUNCTION IF EXISTS `FN_CalcularRendimientoCaptura`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_CalcularRendimientoCaptura` (`p_captura_id` INT, `p_combustible` DECIMAL(10,2), `p_tripulantes` INT) RETURNS DECIMAL(10,2)  BEGIN
  DECLARE total_kg DECIMAL(10,2);
  SELECT SUM(cantidad_kg) INTO total_kg FROM captura_detalle WHERE captura_id = p_captura_id;
  RETURN total_kg / (p_combustible * p_tripulantes);
END$$

DROP FUNCTION IF EXISTS `FN_CalcularValorCaptura`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_CalcularValorCaptura` (`p_captura_id` INT) RETURNS DECIMAL(10,2)  BEGIN
  DECLARE total DECIMAL(10,2);
  SELECT SUM(cd.cantidad_kg * e.precio_kg) INTO total
  FROM captura_detalle cd
  JOIN especies e ON cd.especie_id = e.id
  WHERE cd.captura_id = p_captura_id;
  RETURN total;
END$$

DROP FUNCTION IF EXISTS `FN_ObtenerIndicadoresTemporada`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_ObtenerIndicadoresTemporada` (`p_anio` INT) RETURNS DECIMAL(10,2)  BEGIN
  DECLARE promedio DECIMAL(10,2);
  SELECT AVG(cd.cantidad_kg) INTO promedio
  FROM captura_detalle cd
  JOIN capturas c ON cd.captura_id = c.id
  WHERE YEAR(c.fecha_inicio) = p_anio;
  RETURN promedio;
END$$

DROP FUNCTION IF EXISTS `FN_ObtenerMejorZonaPesca`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_ObtenerMejorZonaPesca` (`p_especie_id` INT) RETURNS VARCHAR(100) CHARSET utf8mb4  BEGIN
  DECLARE zona VARCHAR(100);
  SELECT z.nombre INTO zona
  FROM captura_detalle cd
  JOIN capturas c ON cd.captura_id = c.id
  JOIN zonas_pesca z ON c.zona_id = z.id
  WHERE cd.especie_id = p_especie_id
  GROUP BY z.nombre
  ORDER BY SUM(cd.cantidad_kg) DESC
  LIMIT 1;
  RETURN zona;
END$$

DROP FUNCTION IF EXISTS `FN_VerificarDisponibilidadEmbarcacion`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `FN_VerificarDisponibilidadEmbarcacion` (`p_embarcacion_id` INT) RETURNS TINYINT(1)  BEGIN
  DECLARE ocupado INT;
  SELECT COUNT(*) INTO ocupado FROM capturas 
  WHERE embarcacion_id = p_embarcacion_id AND fecha_fin IS NULL;
  RETURN ocupado = 0;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asignaciones_tripulantes`
--

DROP TABLE IF EXISTS `asignaciones_tripulantes`;
CREATE TABLE IF NOT EXISTS `asignaciones_tripulantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tripulante_id` int NOT NULL,
  `embarcacion_id` int NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `cargo_a_bordo` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tripulante_id` (`tripulante_id`),
  KEY `embarcacion_id` (`embarcacion_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `asignaciones_tripulantes`
--

INSERT INTO `asignaciones_tripulantes` (`id`, `tripulante_id`, `embarcacion_id`, `fecha_inicio`, `fecha_fin`, `cargo_a_bordo`) VALUES
(1, 1, 1, '2024-01-01', '2024-12-31', 'Capitán'),
(2, 2, 1, '2024-01-01', '2024-12-31', 'Primer Oficial'),
(3, 3, 1, '2024-01-01', '2024-12-31', 'Jefe de Máquinas'),
(4, 4, 2, '2024-02-01', '2024-08-01', 'Marinero'),
(5, 5, 3, '2024-03-01', NULL, 'Marinero'),
(6, 6, 9, '2024-01-01', '2024-12-31', 'Capitán'),
(7, 7, 5, '2024-02-15', '2024-09-15', 'Cocinero'),
(8, 8, 3, '2024-04-01', '2024-10-01', 'Primer Oficial'),
(9, 9, 6, '2024-03-01', '2024-12-01', 'Jefe de Máquinas'),
(10, 10, 11, '2024-05-01', '2024-09-01', 'Marinera'),
(11, 11, 4, '2024-06-01', NULL, 'Marinero'),
(12, 12, 12, '2024-07-01', '2024-12-31', 'Capitán');

--
-- Disparadores `asignaciones_tripulantes`
--
DROP TRIGGER IF EXISTS `TR_VerificarCertificacionesTripulantes`;
DELIMITER $$
CREATE TRIGGER `TR_VerificarCertificacionesTripulantes` BEFORE INSERT ON `asignaciones_tripulantes` FOR EACH ROW BEGIN
  DECLARE v_certificados INT DEFAULT 0;

  SELECT COUNT(*) INTO v_certificados
  FROM tripulante_certificados
  WHERE tripulante_id = NEW.tripulante_id
    AND (fecha_vencimiento IS NULL OR fecha_vencimiento >= CURDATE());

  IF v_certificados = 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'El tripulante no tiene certificaciones válidas.';
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `capturas`
--

DROP TABLE IF EXISTS `capturas`;
CREATE TABLE IF NOT EXISTS `capturas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_registro` varchar(60) NOT NULL,
  `embarcacion_id` int NOT NULL,
  `zona_id` int NOT NULL,
  `fecha_inicio` datetime DEFAULT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `metodo_pesca` varchar(80) DEFAULT NULL,
  `condiciones_climaticas` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_registro` (`numero_registro`),
  KEY `embarcacion_id` (`embarcacion_id`),
  KEY `zona_id` (`zona_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `capturas`
--

INSERT INTO `capturas` (`id`, `numero_registro`, `embarcacion_id`, `zona_id`, `fecha_inicio`, `fecha_fin`, `metodo_pesca`, `condiciones_climaticas`) VALUES
(1, 'CAP-20240201-01', 1, 1, '2024-02-01 06:00:00', '2024-02-01 18:00:00', 'arrastre', 'viento 5 nudos'),
(2, 'CAP-20240205-01', 2, 3, '2024-02-05 04:00:00', '2024-02-05 14:00:00', 'cerco', 'mar calma'),
(3, 'CAP-20240210-01', 3, 4, '2024-02-10 05:00:00', '2024-02-10 20:00:00', 'palangre', 'bruma ligera'),
(4, 'CAP-20240215-01', 4, 2, '2024-02-15 07:00:00', '2024-02-15 15:00:00', 'cerco', 'corriente moderada'),
(5, 'CAP-20240220-01', 5, 1, '2024-02-20 06:30:00', '2024-02-20 19:00:00', 'arrastre', 'mar agitado'),
(6, 'CAP-20240225-01', 6, 4, '2024-02-25 05:30:00', '2024-02-25 18:30:00', 'palangre', 'viento fuerte'),
(7, 'CAP-20240301-01', 7, 5, '2024-03-01 06:00:00', '2024-03-01 16:00:00', 'artesanal', 'buen tiempo'),
(8, 'CAP-20240305-01', 8, 6, '2024-03-05 05:00:00', '2024-03-05 13:00:00', 'cerco', 'mar calma'),
(9, 'CAP-20240401-01', 9, 1, '2024-04-01 06:00:00', '2024-04-01 20:00:00', 'arrastre', 'brisa'),
(10, 'CAP-20240405-01', 10, 4, '2024-04-05 04:00:00', '2024-04-05 18:00:00', 'palangre', 'nublado'),
(11, 'CAP-20240501-01', 11, 6, '2024-05-01 06:00:00', '2024-05-01 12:00:00', 'cerco', 'mar calma'),
(12, 'CAP-20240505-01', 12, 5, '2024-05-05 05:00:00', '2024-05-05 14:00:00', 'artesanal', 'bruma');

--
-- Disparadores `capturas`
--
DROP TRIGGER IF EXISTS `TR_ActualizarHistorialEmbarcacion`;
DELIMITER $$
CREATE TRIGGER `TR_ActualizarHistorialEmbarcacion` AFTER INSERT ON `capturas` FOR EACH ROW BEGIN
  INSERT INTO historial_embarcacion(embarcacion_id, fecha, evento)
  VALUES(NEW.embarcacion_id, NOW(), 'Nueva captura registrada');
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `captura_detalle`
--

DROP TABLE IF EXISTS `captura_detalle`;
CREATE TABLE IF NOT EXISTS `captura_detalle` (
  `captura_id` int NOT NULL,
  `especie_id` int NOT NULL,
  `cantidad_kg` decimal(12,2) NOT NULL,
  PRIMARY KEY (`captura_id`,`especie_id`),
  KEY `especie_id` (`especie_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `captura_detalle`
--

INSERT INTO `captura_detalle` (`captura_id`, `especie_id`, `cantidad_kg`) VALUES
(1, 1, 2000.00),
(1, 8, 500.00),
(2, 4, 800.00),
(3, 1, 1200.00),
(4, 2, 400.00),
(5, 5, 600.00),
(6, 6, 900.00),
(7, 11, 300.00),
(8, 8, 1200.00),
(9, 1, 5000.00),
(10, 10, 200.00),
(11, 4, 700.00);

--
-- Disparadores `captura_detalle`
--
DROP TRIGGER IF EXISTS `TR_VerificarCuotaPesca`;
DELIMITER $$
CREATE TRIGGER `TR_VerificarCuotaPesca` BEFORE INSERT ON `captura_detalle` FOR EACH ROW BEGIN
  DECLARE v_cuota DECIMAL(10,2);
  SELECT cuota_disponible INTO v_cuota FROM cuotas WHERE especie_id = NEW.especie_id;
  IF v_cuota < NEW.cantidad_kg THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cuota excedida para esta especie';
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `certificados`
--

DROP TABLE IF EXISTS `certificados`;
CREATE TABLE IF NOT EXISTS `certificados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `certificados`
--

INSERT INTO `certificados` (`id`, `codigo`, `descripcion`) VALUES
(1, 'CERT-001', 'Capacitacion Básica de Seguridad'),
(2, 'CERT-002', 'Patrón de Embarcación'),
(3, 'CERT-003', 'Mecánica Marina'),
(4, 'CERT-004', 'Manipulación de Alimentos'),
(5, 'CERT-005', 'Primeros Auxilios'),
(6, 'CERT-006', 'Tripulación Avanzada'),
(7, 'CERT-007', 'Certificado Radar'),
(8, 'CERT-008', 'Certificado AIS'),
(9, 'CERT-009', 'Certificado Buceo'),
(10, 'CERT-010', 'Certificado Conservación'),
(11, 'CERT-011', 'Licencia de Radio'),
(12, 'CERT-012', 'Formación Ambiental');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `control_calidad`
--

DROP TABLE IF EXISTS `control_calidad`;
CREATE TABLE IF NOT EXISTS `control_calidad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lote_codigo` varchar(60) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `parametros_analizados` text,
  `resultados` text,
  `cumple_standards` tinyint(1) DEFAULT NULL,
  `inspector` varchar(100) DEFAULT NULL,
  `decision` enum('aprobado','rechazado','cuarentena') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `lote_codigo` (`lote_codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `control_calidad`
--

INSERT INTO `control_calidad` (`id`, `lote_codigo`, `fecha`, `parametros_analizados`, `resultados`, `cumple_standards`, `inspector`, `decision`) VALUES
(1, 'LOT-0001', '2024-02-03', 'temp, ph', 'OK', 1, 'Inspector A', 'aprobado'),
(2, 'LOT-0002', '2024-02-07', 'temp, sal', 'OK', 1, 'Inspector B', 'aprobado'),
(3, 'LOT-0003', '2024-02-12', 'temp', 'OK', 1, 'Inspector C', 'aprobado'),
(4, 'LOT-0004', '2024-02-17', 'microbiologia', 'nivel alto', 0, 'Inspector D', 'rechazado'),
(5, 'LOT-0005', '2024-02-22', 'rendimiento', 'bajo', 0, 'Inspector E', 'cuarentena'),
(6, 'LOT-0006', '2024-02-27', 'temp', 'OK', 1, 'Inspector A', 'aprobado'),
(7, 'LOT-0007', '2024-03-03', 'temp', 'OK', 1, 'Inspector C', 'aprobado'),
(8, 'LOT-0008', '2024-03-07', 'imagen', 'OK', 1, 'Inspector B', 'aprobado'),
(9, 'LOT-0009', '2024-04-03', 'temp', 'OK', 1, 'Inspector A', 'aprobado'),
(10, 'LOT-0010', '2024-04-07', 'ph', 'OK', 1, 'Inspector D', 'aprobado'),
(11, 'LOT-0011', '2024-05-03', 'sal', 'OK', 1, 'Inspector B', 'aprobado'),
(12, 'LOT-0012', '2024-05-07', 'temp', 'OK', 1, 'Inspector A', 'aprobado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cuotas`
--

DROP TABLE IF EXISTS `cuotas`;
CREATE TABLE IF NOT EXISTS `cuotas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `temporada_id` int NOT NULL,
  `especie_id` int NOT NULL,
  `cuota_kg` decimal(12,2) NOT NULL,
  `cuota_restante_kg` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `temporada_id` (`temporada_id`,`especie_id`),
  KEY `especie_id` (`especie_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `cuotas`
--

INSERT INTO `cuotas` (`id`, `temporada_id`, `especie_id`, `cuota_kg`, `cuota_restante_kg`) VALUES
(1, 1, 1, 10000.00, 10000.00),
(2, 1, 2, 5000.00, 5000.00),
(3, 2, 4, 8000.00, 8000.00),
(4, 3, 5, 3000.00, 3000.00),
(5, 4, 1, 12000.00, 12000.00),
(6, 5, 10, 1000.00, 1000.00),
(7, 6, 2, 2000.00, 2000.00),
(8, 7, 3, 1200.00, 1200.00),
(9, 8, 7, 500.00, 500.00),
(10, 9, 8, 6000.00, 6000.00),
(11, 2, 9, 2000.00, 2000.00),
(12, 11, 1, 3000.00, 3000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `embarcaciones`
--

DROP TABLE IF EXISTS `embarcaciones`;
CREATE TABLE IF NOT EXISTS `embarcaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `matricula` varchar(30) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` enum('arrastrero','cerquero','palangrero','otro') DEFAULT NULL,
  `ano_construccion` year DEFAULT NULL,
  `material_casco` varchar(50) DEFAULT NULL,
  `eslora` decimal(6,2) DEFAULT NULL,
  `manga` decimal(6,2) DEFAULT NULL,
  `calado` decimal(6,2) DEFAULT NULL,
  `capacidad_bodega_tn` decimal(8,2) DEFAULT NULL,
  `potencia_motor_kw` int DEFAULT NULL,
  `velocidad_max_kn` decimal(5,2) DEFAULT NULL,
  `autonomia_dias` int DEFAULT NULL,
  `equipos_navegacion` text,
  `fecha_ultima_inspeccion` date DEFAULT NULL,
  `estado` enum('operativa','mantenimiento','baja') DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricula` (`matricula`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `embarcaciones`
--

INSERT INTO `embarcaciones` (`id`, `matricula`, `nombre`, `tipo`, `ano_construccion`, `material_casco`, `eslora`, `manga`, `calado`, `capacidad_bodega_tn`, `potencia_motor_kw`, `velocidad_max_kn`, `autonomia_dias`, `equipos_navegacion`, `fecha_ultima_inspeccion`, `estado`) VALUES
(1, 'MAT-001', 'Marinero I', 'arrastrero', '2005', 'Acero', 45.00, 8.50, 4.60, 120.00, 1500, 14.50, 20, 'Radar, GPS', '2025-06-10', 'operativa'),
(2, 'MAT-002', 'Océano Rey', 'cerquero', '2010', 'Fibra', 38.50, 7.20, 3.80, 80.00, 900, 12.00, 15, 'GPS, Eco-sonar', '2025-03-15', 'operativa'),
(3, 'MAT-003', 'Neptuno', 'palangrero', '2012', 'Acero', 50.00, 9.00, 5.00, 150.00, 1800, 15.20, 25, 'Radar, AIS', '2024-11-02', 'operativa'),
(4, 'MAT-004', 'Brisa', 'cerquero', '2018', 'Aluminio', 30.00, 6.50, 3.20, 45.00, 650, 11.50, 10, 'GPS', '2025-01-20', 'operativa'),
(5, 'MAT-005', 'Aurora', 'arrastrero', '2000', 'Acero', 48.00, 8.80, 4.90, 140.00, 1600, 13.50, 30, 'Radar', '2024-12-01', 'mantenimiento'),
(6, 'MAT-006', 'Tridente', 'palangrero', '2015', 'Acero', 46.00, 8.00, 4.50, 110.00, 1400, 13.00, 18, 'GPS, Radar', '2025-08-12', 'operativa'),
(7, 'MAT-007', 'Viento', 'otro', '2008', 'Fibra', 22.00, 5.00, 2.50, 20.00, 300, 10.00, 7, 'GPS', '2025-07-18', 'operativa'),
(8, 'MAT-008', 'Sirena', 'cerquero', '2011', 'Acero', 33.00, 6.80, 3.40, 60.00, 700, 11.80, 12, 'Eco-sonar', '2025-05-05', 'operativa'),
(9, 'MAT-009', 'Albatros', 'arrastrero', '1999', 'Acero', 55.00, 10.00, 5.50, 200.00, 2000, 16.00, 40, 'Radar, GPS, AIS', '2025-09-09', 'operativa'),
(10, 'MAT-010', 'Pacifico', 'palangrero', '2003', 'Acero', 42.00, 7.80, 4.00, 95.00, 1200, 12.50, 16, 'GPS, AIS', '2025-02-02', 'operativa'),
(11, 'MAT-011', 'Costa Linda', 'cerquero', '2019', 'Aluminio', 28.00, 6.00, 3.00, 35.00, 500, 10.50, 8, 'GPS', '2025-04-01', 'operativa'),
(12, 'MAT-012', 'Fuego Marino', 'otro', '2016', 'Fibra', 18.00, 4.50, 2.20, 12.00, 200, 9.00, 5, 'GPS', '2025-08-01', 'operativa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipos_pesca`
--

DROP TABLE IF EXISTS `equipos_pesca`;
CREATE TABLE IF NOT EXISTS `equipos_pesca` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `tipo` enum('red','anzuelos','trampa','otros') DEFAULT NULL,
  `caracteristicas` text,
  `fecha_adquisicion` date DEFAULT NULL,
  `costo` decimal(12,2) DEFAULT NULL,
  `vida_util_anios` int DEFAULT NULL,
  `embarcacion_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `embarcacion_id` (`embarcacion_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `equipos_pesca`
--

INSERT INTO `equipos_pesca` (`id`, `codigo`, `tipo`, `caracteristicas`, `fecha_adquisicion`, `costo`, `vida_util_anios`, `embarcacion_id`) VALUES
(1, 'EQ-001', 'red', 'Red arrastre 200m', '2015-01-01', 50000.00, 10, 1),
(2, 'EQ-002', 'anzuelos', 'Línea de palangre 1000 anzuelos', '2018-06-06', 20000.00, 8, 3),
(3, 'EQ-003', 'trampa', 'Trampas para crustáceos', '2019-03-03', 8000.00, 6, 2),
(4, 'EQ-004', 'red', 'Red de cerco 150m', '2020-07-07', 30000.00, 7, 2),
(5, 'EQ-005', 'anzuelos', 'Palangre pequeño', '2017-09-09', 12000.00, 8, 6),
(6, 'EQ-006', 'trampa', 'Trampa experimental', '2021-02-02', 5000.00, 5, NULL),
(7, 'EQ-007', 'red', 'Red auxiliar', '2016-12-12', 10000.00, 6, 5),
(8, 'EQ-008', 'anzuelos', 'Anzuelos especiales', '2022-05-05', 7000.00, 5, 10),
(9, 'EQ-009', 'otros', 'Sonda profunda', '2014-04-04', 15000.00, 12, 9),
(10, 'EQ-010', 'red', 'Red de repuesto', '2013-08-08', 9000.00, 9, 11),
(11, 'EQ-011', 'trampa', 'Trampas costeras', '2018-10-10', 6000.00, 6, 8),
(12, 'EQ-012', 'otros', 'Equipo de AIS', '2020-01-01', 4000.00, 10, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `especies`
--

DROP TABLE IF EXISTS `especies`;
CREATE TABLE IF NOT EXISTS `especies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `nombre_cientifico` varchar(150) DEFAULT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `especies`
--

INSERT INTO `especies` (`id`, `nombre`, `nombre_cientifico`, `descripcion`) VALUES
(1, 'Atún', 'Thunnus albacares', 'Atún de alta demanda'),
(2, 'Merluza', 'Merluccius hubbsi', 'Pez blanco común'),
(3, 'Salmón', 'Salmo salar', 'Salmón atlántico'),
(4, 'Sardina', 'Sardinops sagax', 'Pequeña pelágica'),
(5, 'Bacalao', 'Gadus morhua', 'Fondo marino'),
(6, 'Calamar', 'Loligo vulgaris', 'Cephalópodo'),
(7, 'Lenguado', 'Solea solea', 'Pez plano'),
(8, 'Caballa', 'Scomber scombrus', 'Pelágico migratorio'),
(9, 'Camarón', 'Penaeus vannamei', 'Crustáceo'),
(10, 'Pargo', 'Lutjanus spp.', 'Demanda local'),
(11, 'Corvina', 'Cilus gilberti', 'Especie costera'),
(12, 'Raya', 'Dasyatis pastinaca', 'Cartilaginoso');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `licencias`
--

DROP TABLE IF EXISTS `licencias`;
CREATE TABLE IF NOT EXISTS `licencias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_licencia` varchar(50) NOT NULL,
  `embarcacion_id` int NOT NULL,
  `tipo_licencia` varchar(50) DEFAULT NULL,
  `fecha_emision` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `autoridad_emisora` varchar(100) DEFAULT NULL,
  `zonas_permitidas` text,
  `cuotas_asignadas` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_licencia` (`numero_licencia`),
  KEY `embarcacion_id` (`embarcacion_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `licencias`
--

INSERT INTO `licencias` (`id`, `numero_licencia`, `embarcacion_id`, `tipo_licencia`, `fecha_emision`, `fecha_vencimiento`, `autoridad_emisora`, `zonas_permitidas`, `cuotas_asignadas`) VALUES
(1, 'LIC-2024-001', 1, 'Comercial', '2024-01-01', '2026-01-01', 'Autoridad Marina', 'Z1,Z2', 'Atún:5000'),
(2, 'LIC-2024-002', 2, 'Artesanal', '2023-06-15', '2025-06-15', 'Autoridad Regional', 'Z3', 'Merluza:2000'),
(3, 'LIC-2024-003', 3, 'Comercial', '2024-03-10', '2025-03-09', 'Autoridad Marina', 'Z1,Z4', 'Salmón:1000'),
(4, 'LIC-2024-004', 4, 'Artesanal', '2024-02-01', '2025-02-01', 'Autoridad Local', 'Z2', 'Sardina:1500'),
(5, 'LIC-2024-005', 5, 'Comercial', '2022-09-01', '2024-09-01', 'Autoridad Marina', 'Z1,Z2', 'Bacalao:800'),
(6, 'LIC-2024-006', 6, 'Comercial', '2024-05-05', '2026-05-05', 'Autoridad Marina', 'Z4', 'Calamar:2000'),
(7, 'LIC-2024-007', 7, 'Recreativa', '2024-07-01', '2025-07-01', 'Autoridad Local', 'Z5', ''),
(8, 'LIC-2024-008', 8, 'Artesanal', '2023-11-11', '2024-11-11', 'Autoridad Regional', 'Z3,Z6', 'Caballa:1000'),
(9, 'LIC-2024-009', 9, 'Comercial', '2024-08-08', '2026-08-08', 'Autoridad Marina', 'Z1,Z2,Z4', 'Atún:8000'),
(10, 'LIC-2024-010', 10, 'Comercial', '2022-04-04', '2024-04-04', 'Autoridad Marina', 'Z4', 'Pargo:500'),
(11, 'LIC-2024-011', 11, 'Artesanal', '2024-02-20', '2025-02-20', 'Autoridad Local', 'Z6', 'Corvina:300'),
(12, 'LIC-2024-012', 12, 'Recreativa', '2024-06-06', '2025-06-06', 'Autoridad Local', 'Z5', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `licencia_especies`
--

DROP TABLE IF EXISTS `licencia_especies`;
CREATE TABLE IF NOT EXISTS `licencia_especies` (
  `licencia_id` int NOT NULL,
  `especie_id` int NOT NULL,
  PRIMARY KEY (`licencia_id`,`especie_id`),
  KEY `especie_id` (`especie_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `licencia_especies`
--

INSERT INTO `licencia_especies` (`licencia_id`, `especie_id`) VALUES
(1, 1),
(1, 8),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(8, 8),
(9, 1),
(9, 8),
(10, 10),
(11, 11);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mantenimientos`
--

DROP TABLE IF EXISTS `mantenimientos`;
CREATE TABLE IF NOT EXISTS `mantenimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipo_id` int DEFAULT NULL,
  `embarcacion_id` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `tipo_mantenimiento` varchar(80) DEFAULT NULL,
  `descripcion` text,
  `repuestos_utilizados` text,
  `costo` decimal(12,2) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipo_id` (`equipo_id`),
  KEY `embarcacion_id` (`embarcacion_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `mantenimientos`
--

INSERT INTO `mantenimientos` (`id`, `equipo_id`, `embarcacion_id`, `fecha`, `tipo_mantenimiento`, `descripcion`, `repuestos_utilizados`, `costo`, `responsable`) VALUES
(1, 1, 1, '2025-07-01', 'Preventivo', 'Cambio de cables', 'cables', 1500.00, 'Taller Mar'),
(2, 2, 3, '2025-06-15', 'Correctivo', 'Reparación motores', 'motores', 5000.00, 'Mecánico S.A.'),
(3, 3, 2, '2025-04-10', 'Preventivo', 'Revisión trampas', 'mallas', 300.00, 'Tecnico Local'),
(4, 4, 2, '2025-05-05', 'Preventivo', 'Inspección red cerco', NULL, 200.00, 'Taller Mar'),
(5, 5, 6, '2025-03-12', 'Correctivo', 'Cambio anzuelos', NULL, 150.00, 'Mecánico S.A.'),
(6, 6, NULL, '2025-01-20', 'Preventivo', 'Ajustes trapas', 'mallas', 100.00, 'Taller Mar'),
(7, 7, 5, '2024-12-01', 'Correctivo', 'Reparación cabos', 'cabos', 400.00, 'Taller Mar'),
(8, 8, 10, '2025-02-02', 'Preventivo', 'Chequeo', NULL, 80.00, 'Tecnico Local'),
(9, 9, 9, '2025-09-09', 'Instrumental', 'Calibración sonda', NULL, 600.00, 'Proveedor X'),
(10, 10, 11, '2025-04-14', 'Preventivo', 'Cambio mallas', NULL, 250.00, 'Taller Mar'),
(11, 11, 8, '2025-05-21', 'Correctivo', 'Reemplazo piezas', NULL, 350.00, 'Mecánico S.A.'),
(12, 12, 4, '2025-08-01', 'Preventivo', 'Actualización AIS', NULL, 200.00, 'Proveedor X');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `procesamiento`
--

DROP TABLE IF EXISTS `procesamiento`;
CREATE TABLE IF NOT EXISTS `procesamiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lote_codigo` varchar(60) NOT NULL,
  `captura_id` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `especie_id` int DEFAULT NULL,
  `materia_prima_kg` decimal(12,2) DEFAULT NULL,
  `metodo_procesamiento` enum('congelado','enlatado','salado','otro') DEFAULT NULL,
  `rendimiento` decimal(6,2) DEFAULT NULL,
  `tipo_producto_final` varchar(100) DEFAULT NULL,
  `cantidad_producida_kg` decimal(12,2) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lote_codigo` (`lote_codigo`),
  KEY `captura_id` (`captura_id`),
  KEY `especie_id` (`especie_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `procesamiento`
--

INSERT INTO `procesamiento` (`id`, `lote_codigo`, `captura_id`, `fecha`, `especie_id`, `materia_prima_kg`, `metodo_procesamiento`, `rendimiento`, `tipo_producto_final`, `cantidad_producida_kg`, `responsable`) VALUES
(1, 'LOT-0001', 1, '2024-02-02', 1, 1500.00, 'congelado', 60.00, 'Atún en filete', 900.00, 'Jefe Planta'),
(2, 'LOT-0002', 2, '2024-02-06', 4, 700.00, 'enlatado', 55.00, 'Sardina en lata', 385.00, 'Jefe Planta'),
(3, 'LOT-0003', 3, '2024-02-11', 1, 1000.00, 'congelado', 58.00, 'Atún filete', 580.00, 'Jefe Planta'),
(4, 'LOT-0004', 4, '2024-02-16', 2, 350.00, 'congelado', 62.00, 'Merluza filete', 217.00, 'Jefe Planta'),
(5, 'LOT-0005', 5, '2024-02-21', 5, 500.00, 'salado', 45.00, 'Bacalao salado', 225.00, 'Jefe Planta'),
(6, 'LOT-0006', 6, '2024-02-26', 6, 800.00, 'congelado', 50.00, 'Calamar entero', 400.00, 'Jefe Planta'),
(7, 'LOT-0007', 7, '2024-03-02', 11, 250.00, 'congelado', 65.00, 'Corvina filete', 162.50, 'Jefe Planta'),
(8, 'LOT-0008', 8, '2024-03-06', 8, 1000.00, 'congelado', 60.00, 'Caballa filete', 600.00, 'Jefe Planta'),
(9, 'LOT-0009', 9, '2024-04-02', 1, 4000.00, 'congelado', 59.00, 'Atún entero', 2360.00, 'Jefe Planta'),
(10, 'LOT-0010', 10, '2024-04-06', 10, 180.00, 'congelado', 63.00, 'Pargo filete', 113.40, 'Jefe Planta'),
(11, 'LOT-0011', 11, '2024-05-02', 4, 600.00, 'enlatado', 54.00, 'Sardina en lata', 324.00, 'Jefe Planta'),
(12, 'LOT-0012', 12, '2024-05-06', 9, 120.00, 'congelado', 55.00, 'Camarón congelado', 66.00, 'Jefe Planta');

--
-- Disparadores `procesamiento`
--
DROP TRIGGER IF EXISTS `TR_ActualizarInventarioProcesado`;
DELIMITER $$
CREATE TRIGGER `TR_ActualizarInventarioProcesado` AFTER INSERT ON `procesamiento` FOR EACH ROW BEGIN
  INSERT INTO inventario(producto, cantidad_kg, fecha_ingreso)
  VALUES(CONCAT('Lote_', NEW.id), NEW.rendimiento, NOW());
END
$$
DELIMITER ;
DROP TRIGGER IF EXISTS `TR_ControlarCalidadProcesamiento`;
DELIMITER $$
CREATE TRIGGER `TR_ControlarCalidadProcesamiento` AFTER INSERT ON `procesamiento` FOR EACH ROW BEGIN
  IF NEW.rendimiento < 70 THEN
    INSERT INTO alertas(tipo, descripcion, fecha)
    VALUES('Calidad', CONCAT('Rendimiento bajo en captura ', NEW.captura_id), NOW());
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos_procesados`
--

DROP TABLE IF EXISTS `productos_procesados`;
CREATE TABLE IF NOT EXISTS `productos_procesados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo_producto` varchar(80) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `tipo_procesamiento` varchar(80) DEFAULT NULL,
  `presentacion` varchar(80) DEFAULT NULL,
  `empaque` varchar(80) DEFAULT NULL,
  `peso_neto_g` decimal(8,2) DEFAULT NULL,
  `fecha_produccion` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `temp_conservacion_c` decimal(5,2) DEFAULT NULL,
  `precio` decimal(12,2) DEFAULT NULL,
  `lote_codigo` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_producto` (`codigo_producto`),
  KEY `lote_codigo` (`lote_codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `productos_procesados`
--

INSERT INTO `productos_procesados` (`id`, `codigo_producto`, `descripcion`, `tipo_procesamiento`, `presentacion`, `empaque`, `peso_neto_g`, `fecha_produccion`, `fecha_vencimiento`, `temp_conservacion_c`, `precio`, `lote_codigo`) VALUES
(1, 'PR-LOT1', 'Atún filete 1kg', 'congelado', 'filete', 'caja', 1000.00, '2024-02-02', '2025-02-02', -18.00, 10.00, 'LOT-0001'),
(2, 'PR-LOT2', 'Sardina lata 200g', 'enlatado', 'lata', 'pack', 200.00, '2024-02-06', '2026-02-06', 5.00, 1.50, 'LOT-0002'),
(3, 'PR-LOT3', 'Atún filete 500g', 'congelado', 'filete', 'caja', 500.00, '2024-02-11', '2025-02-11', -18.00, 6.00, 'LOT-0003'),
(4, 'PR-LOT4', 'Merluza 1kg', 'congelado', 'filete', 'caja', 1000.00, '2024-02-17', '2025-02-17', -18.00, 8.00, 'LOT-0004'),
(5, 'PR-LOT5', 'Bacalao salado 1kg', 'salado', 'pieza', 'saco', 1000.00, '2024-02-22', '2025-02-22', 10.00, 9.00, 'LOT-0005'),
(6, 'PR-LOT6', 'Calamar 1kg', 'congelado', 'entero', 'caja', 1000.00, '2024-02-27', '2025-02-27', -18.00, 7.00, 'LOT-0006'),
(7, 'PR-LOT7', 'Corvina 500g', 'congelado', 'filete', 'caja', 500.00, '2024-03-03', '2025-03-03', -18.00, 5.00, 'LOT-0007'),
(8, 'PR-LOT8', 'Caballa 1kg', 'congelado', 'filete', 'caja', 1000.00, '2024-03-07', '2025-03-07', -18.00, 4.00, 'LOT-0008'),
(9, 'PR-LOT9', 'Atún entero 10kg', 'congelado', 'entero', 'caja', 10000.00, '2024-04-03', '2025-04-03', -18.00, 80.00, 'LOT-0009'),
(10, 'PR-LOT10', 'Pargo 1kg', 'congelado', 'filete', 'caja', 1000.00, '2024-04-07', '2025-04-07', -18.00, 6.00, 'LOT-0010'),
(11, 'PR-LOT11', 'Sardina lata 400g', 'enlatado', 'lata', 'pack', 400.00, '2024-05-03', '2026-05-03', 5.00, 2.50, 'LOT-0011'),
(12, 'PR-LOT12', 'Camarón 500g', 'congelado', 'bag', 'bolsa', 500.00, '2024-05-07', '2025-05-07', -18.00, 6.00, 'LOT-0012');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `temporadas`
--

DROP TABLE IF EXISTS `temporadas`;
CREATE TABLE IF NOT EXISTS `temporadas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `especies_permitidas` text,
  `cuotas_globales` text,
  `metodos_autorizados` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `temporadas`
--

INSERT INTO `temporadas` (`id`, `nombre`, `fecha_inicio`, `fecha_fin`, `especies_permitidas`, `cuotas_globales`, `metodos_autorizados`) VALUES
(1, 'Temporada 2024-1', '2024-01-01', '2024-06-30', 'Atún,Merluza,Salmón', 'Atún:10000,Merluza:5000', 'arrastre,palangre,cerco'),
(2, 'Temporada 2024-2', '2024-07-01', '2024-12-31', 'Sardina,Camarón', 'Sardina:8000,Camarón:2000', 'cerco,artesanal'),
(3, 'Temporada 2023-1', '2023-01-01', '2023-06-30', 'Bacalao,Calamar', 'Bacalao:3000,Calamar:4000', 'palangre,arrastre'),
(4, 'Temporada 2025-1', '2025-01-01', '2025-06-30', 'Atún,Calamar', 'Atún:12000,Calamar:5000', 'arrastre,palangre'),
(5, 'Temporada 2024-3', '2024-09-01', '2024-11-30', 'Pargo,Corvina', 'Pargo:1000,Corvina:800', 'artesanal'),
(6, 'Temporada 2024-4', '2024-02-01', '2024-02-28', 'Merluza', 'Merluza:2000', 'artesanal'),
(7, 'Temporada 2024-5', '2024-03-01', '2024-05-31', 'Salmón', 'Salmón:1200', 'palangre'),
(8, 'Temporada 2024-6', '2024-10-01', '2024-12-31', 'Lenguado,Raya', 'Lenguado:500,Raya:300', 'artesanal'),
(9, 'Temporada 2023-2', '2023-07-01', '2023-12-31', 'Caballa,Sardina', 'Caballa:6000,Sardina:7000', 'cerco'),
(10, 'Temporada 2024-7', '2024-06-01', '2024-06-30', 'Atún', 'Atún:2000', 'palangre'),
(11, 'Temporada 2022-1', '2022-01-01', '2022-12-31', 'Varios', 'Varios', 'varios'),
(12, 'Temporada 2024-8', '2024-04-01', '2024-04-30', 'Camarón', 'Camarón:1500', 'artesanal');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tripulantes`
--

DROP TABLE IF EXISTS `tripulantes`;
CREATE TABLE IF NOT EXISTS `tripulantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dni` varchar(30) NOT NULL,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  `libreta_embarque` varchar(50) DEFAULT NULL,
  `cargo` varchar(80) DEFAULT NULL,
  `experiencia_anios` int DEFAULT NULL,
  `estado_salud` varchar(100) DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dni` (`dni`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `tripulantes`
--

INSERT INTO `tripulantes` (`id`, `dni`, `nombres`, `apellidos`, `fecha_nacimiento`, `direccion`, `telefono`, `libreta_embarque`, `cargo`, `experiencia_anios`, `estado_salud`, `disponible`) VALUES
(1, 'DNI001', 'Carlos', 'Perez', '1980-05-12', 'Av. Mar 123', '+57-300111222', 'LB-001', 'Capitán', 20, 'Bueno', 1),
(2, 'DNI002', 'Ana', 'Gomez', '1985-07-20', 'Calle 5', '+57-300222333', 'LB-002', 'Primer Oficial', 12, 'Bueno', 1),
(3, 'DNI003', 'Juan', 'Rodriguez', '1978-03-01', 'Barrio Azul', '+57-300333444', 'LB-003', 'Jefe de Máquinas', 18, 'Bueno', 1),
(4, 'DNI004', 'Miguel', 'Lopez', '1990-10-10', 'Puerto Viejo', '+57-300444555', 'LB-004', 'Marinero', 5, 'Bueno', 1),
(5, 'DNI005', 'Luisa', 'Martinez', '1992-12-12', 'Costa 9', '+57-300555666', 'LB-005', 'Marinero', 3, 'Bueno', 1),
(6, 'DNI006', 'Pedro', 'Sanchez', '1975-06-06', 'Col. Marina', '+57-300666777', 'LB-006', 'Capitán', 25, 'Bueno', 1),
(7, 'DNI007', 'Sofia', 'Diaz', '1988-01-01', 'Villa Norte', '+57-300777888', 'LB-007', 'Cocinero', 8, 'Bueno', 1),
(8, 'DNI008', 'Andres', 'Ruiz', '1993-09-09', 'Sector 7', '+57-300888999', 'LB-008', 'Primer Oficial', 6, 'Bueno', 1),
(9, 'DNI009', 'Raul', 'Torres', '1982-02-02', 'Pueblo', '+57-300999000', 'LB-009', 'Jefe de Máquinas', 14, 'Bueno', 1),
(10, 'DNI010', 'María', 'Lozano', '1995-11-11', 'Isla', '+57-300101010', 'LB-010', 'Marinera', 2, 'Bueno', 1),
(11, 'DNI011', 'Diego', 'Ramos', '1987-04-04', 'Puerto Nuevo', '+57-300111333', 'LB-011', 'Marinero', 7, 'Bueno', 1),
(12, 'DNI012', 'Elena', 'Vargas', '1991-08-08', 'Bajada', '+57-300222444', 'LB-012', 'Capitán', 10, 'Bueno', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tripulante_certificados`
--

DROP TABLE IF EXISTS `tripulante_certificados`;
CREATE TABLE IF NOT EXISTS `tripulante_certificados` (
  `tripulante_id` int NOT NULL,
  `certificado_id` int NOT NULL,
  `fecha_emision` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`tripulante_id`,`certificado_id`),
  KEY `certificado_id` (`certificado_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `tripulante_certificados`
--

INSERT INTO `tripulante_certificados` (`tripulante_id`, `certificado_id`, `fecha_emision`, `fecha_vencimiento`) VALUES
(1, 1, '2018-01-01', '2028-01-01'),
(1, 2, '2015-03-01', '2025-03-01'),
(2, 1, '2019-01-01', '2029-01-01'),
(2, 7, '2020-06-06', '2026-06-06'),
(3, 3, '2017-05-05', '2027-05-05'),
(4, 1, '2021-01-01', '2031-01-01'),
(5, 4, '2022-02-02', '2027-02-02'),
(6, 2, '2005-05-05', '2030-05-05'),
(7, 4, '2020-11-11', '2025-11-11'),
(8, 2, '2021-10-10', '2026-10-10'),
(9, 3, '2016-04-04', '2026-04-04'),
(12, 2, '2019-07-07', '2029-07-07');

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_capturasporespecie`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `v_capturasporespecie`;
CREATE TABLE IF NOT EXISTS `v_capturasporespecie` (
`especie` varchar(100)
,`total_kg` decimal(34,2)
,`zona` varchar(100)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_cuotasdisponibles`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `v_cuotasdisponibles`;
CREATE TABLE IF NOT EXISTS `v_cuotasdisponibles` (
`cuota_kg` decimal(12,2)
,`cuota_restante_kg` decimal(12,2)
,`especie` varchar(100)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_estadoflota`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `v_estadoflota`;
CREATE TABLE IF NOT EXISTS `v_estadoflota` (
`capturas_realizadas` bigint
,`estado` enum('operativa','mantenimiento','baja')
,`id` int
,`nombre` varchar(100)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_inventarioproductosprocesados`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `v_inventarioproductosprocesados`;
CREATE TABLE IF NOT EXISTS `v_inventarioproductosprocesados` (
`codigo_producto` varchar(80)
,`descripcion` varchar(200)
,`fecha_procesamiento` date
,`fecha_produccion` date
,`fecha_vencimiento` date
,`id_producto` int
,`lote_codigo` varchar(60)
,`peso_neto_g` decimal(8,2)
,`precio` decimal(12,2)
,`presentacion` varchar(80)
,`rendimiento` decimal(6,2)
,`tipo_procesamiento` varchar(80)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_rendimientoprocesamiento`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `v_rendimientoprocesamiento`;
CREATE TABLE IF NOT EXISTS `v_rendimientoprocesamiento` (
`especie` varchar(100)
,`id` int
,`metodo_procesamiento` enum('congelado','enlatado','salado','otro')
,`rendimiento` decimal(6,2)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `zonas_pesca`
--

DROP TABLE IF EXISTS `zonas_pesca`;
CREATE TABLE IF NOT EXISTS `zonas_pesca` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `coordenadas` varchar(200) DEFAULT NULL,
  `profundidad_promedio_m` decimal(6,2) DEFAULT NULL,
  `temperatura_superficial_c` decimal(5,2) DEFAULT NULL,
  `corrientes_predominantes` varchar(200) DEFAULT NULL,
  `especies_habituales` text,
  `restricciones` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `zonas_pesca`
--

INSERT INTO `zonas_pesca` (`id`, `codigo`, `nombre`, `coordenadas`, `profundidad_promedio_m`, `temperatura_superficial_c`, `corrientes_predominantes`, `especies_habituales`, `restricciones`) VALUES
(1, 'Z1', 'Banco Norte', '-12.45,-77.03', 200.00, 14.50, 'Corriente fría', 'Atún;Caballa;Calamar', 'veda parcial'),
(2, 'Z2', 'Costa Sur', '-13.00,-76.50', 80.00, 16.00, 'Corriente templada', 'Merluza;Pargo', 'reserva marina'),
(3, 'Z3', 'Golfo Este', '-11.90,-76.00', 60.00, 18.20, 'Corriente cálida', 'Sardina;Corvina', 'ninguna'),
(4, 'Z4', 'Estrecho Central', '-12.80,-77.50', 300.00, 12.80, 'Corriente fría y profunda', 'Atún;Bacalao', 'vigilancia'),
(5, 'Z5', 'Islas Menores', '-12.00,-76.20', 25.00, 20.00, 'corriente cálida', 'Camarón;Corvina', 'temporalmente cerrada'),
(6, 'Z6', 'Playa Norte', '-12.20,-77.30', 40.00, 17.50, 'alta productividad', 'Caballa;Sardina', 'ninguna'),
(7, 'Z7', 'Banco Sur', '-13.50,-76.90', 220.00, 13.50, 'corriente fría', 'Lenguado;Raya', 'veda'),
(8, 'Z8', 'Archipiélago', '-12.75,-77.10', 50.00, 19.00, 'corriente cálida', 'Pargo;Corvina', 'zonas protegidas'),
(9, 'Z9', 'Canal Oeste', '-12.90,-77.40', 100.00, 15.00, 'corriente variable', 'Merluza;Calamar', 'ninguna'),
(10, 'Z10', 'Banco Interior', '-13.10,-76.60', 150.00, 14.00, 'corriente fría', 'Atún;Bacalao', 'restricción por tallas'),
(11, 'Z11', 'Bahía Este', '-12.60,-77.20', 30.00, 18.80, 'alta productividad', 'Sardina;Camarón', 'ninguna'),
(12, 'Z12', 'Plataforma Lejana', '-13.90,-76.20', 400.00, 11.50, 'corriente fría profunda', 'Bacalao;Atún', 'cierre temporal');

-- --------------------------------------------------------

--
-- Estructura para la vista `v_capturasporespecie`
--
DROP TABLE IF EXISTS `v_capturasporespecie`;

DROP VIEW IF EXISTS `v_capturasporespecie`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_capturasporespecie`  AS SELECT `es`.`nombre` AS `especie`, `z`.`nombre` AS `zona`, sum(`cd`.`cantidad_kg`) AS `total_kg` FROM (((`captura_detalle` `cd` join `capturas` `c` on((`cd`.`captura_id` = `c`.`id`))) join `zonas_pesca` `z` on((`c`.`zona_id` = `z`.`id`))) join `especies` `es` on((`cd`.`especie_id` = `es`.`id`))) GROUP BY `es`.`nombre`, `z`.`nombre` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_cuotasdisponibles`
--
DROP TABLE IF EXISTS `v_cuotasdisponibles`;

DROP VIEW IF EXISTS `v_cuotasdisponibles`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_cuotasdisponibles`  AS SELECT `e`.`nombre` AS `especie`, `c`.`cuota_kg` AS `cuota_kg`, `c`.`cuota_restante_kg` AS `cuota_restante_kg` FROM (`cuotas` `c` join `especies` `e` on((`c`.`especie_id` = `e`.`id`))) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_estadoflota`
--
DROP TABLE IF EXISTS `v_estadoflota`;

DROP VIEW IF EXISTS `v_estadoflota`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_estadoflota`  AS SELECT `e`.`id` AS `id`, `e`.`nombre` AS `nombre`, `e`.`estado` AS `estado`, count(`c`.`id`) AS `capturas_realizadas` FROM (`embarcaciones` `e` left join `capturas` `c` on((`e`.`id` = `c`.`embarcacion_id`))) GROUP BY `e`.`id`, `e`.`nombre`, `e`.`estado` ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_inventarioproductosprocesados`
--
DROP TABLE IF EXISTS `v_inventarioproductosprocesados`;

DROP VIEW IF EXISTS `v_inventarioproductosprocesados`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_inventarioproductosprocesados`  AS SELECT `p`.`id` AS `id_producto`, `p`.`codigo_producto` AS `codigo_producto`, `p`.`descripcion` AS `descripcion`, `p`.`tipo_procesamiento` AS `tipo_procesamiento`, `p`.`presentacion` AS `presentacion`, `p`.`peso_neto_g` AS `peso_neto_g`, `p`.`fecha_produccion` AS `fecha_produccion`, `p`.`fecha_vencimiento` AS `fecha_vencimiento`, `p`.`precio` AS `precio`, `p`.`lote_codigo` AS `lote_codigo`, `pr`.`fecha` AS `fecha_procesamiento`, `pr`.`rendimiento` AS `rendimiento` FROM (`productos_procesados` `p` left join `procesamiento` `pr` on((`p`.`lote_codigo` = `pr`.`lote_codigo`))) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_rendimientoprocesamiento`
--
DROP TABLE IF EXISTS `v_rendimientoprocesamiento`;

DROP VIEW IF EXISTS `v_rendimientoprocesamiento`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_rendimientoprocesamiento`  AS SELECT `p`.`id` AS `id`, `e`.`nombre` AS `especie`, `p`.`rendimiento` AS `rendimiento`, `p`.`metodo_procesamiento` AS `metodo_procesamiento` FROM (((`procesamiento` `p` join `capturas` `c` on((`p`.`captura_id` = `c`.`id`))) join `captura_detalle` `cd` on((`cd`.`captura_id` = `c`.`id`))) join `especies` `e` on((`cd`.`especie_id` = `e`.`id`))) ;

DELIMITER $$
--
-- Eventos
--
DROP EVENT IF EXISTS `EVT_VerificarLicencias`$$
CREATE DEFINER=`root`@`localhost` EVENT `EVT_VerificarLicencias` ON SCHEDULE EVERY 1 MONTH STARTS '2025-11-01 17:44:38' ON COMPLETION NOT PRESERVE ENABLE DO UPDATE tripulantes SET estado = 'Inactivo'
WHERE licencia_vigencia < CURDATE()$$

DROP EVENT IF EXISTS `EVT_AnalisisCapturaPorZona`$$
CREATE DEFINER=`root`@`localhost` EVENT `EVT_AnalisisCapturaPorZona` ON SCHEDULE EVERY 1 MONTH STARTS '2025-11-01 17:45:20' ON COMPLETION NOT PRESERVE ENABLE DO INSERT INTO reportes(tipo, descripcion, fecha)
VALUES('Analisis Zona', 'Resumen mensual de capturas por zona', NOW())$$

DROP EVENT IF EXISTS `EVT_ControlCalidadProductos`$$
CREATE DEFINER=`root`@`localhost` EVENT `EVT_ControlCalidadProductos` ON SCHEDULE EVERY 15 DAY STARTS '2025-11-01 17:45:41' ON COMPLETION NOT PRESERVE ENABLE DO INSERT INTO controles(tipo, fecha)
VALUES('Calidad de productos', NOW())$$

DROP EVENT IF EXISTS `EVT_ActualizarCondicionesZonas`$$
CREATE DEFINER=`root`@`localhost` EVENT `EVT_ActualizarCondicionesZonas` ON SCHEDULE EVERY 7 DAY STARTS '2025-11-01 17:45:56' ON COMPLETION NOT PRESERVE ENABLE DO UPDATE zonas_pesca SET condiciones = 'Actualizadas', fecha_actualizacion = NOW()$$

DROP EVENT IF EXISTS `EVT_VerificarMantenimientoEquipos`$$
CREATE DEFINER=`root`@`localhost` EVENT `EVT_VerificarMantenimientoEquipos` ON SCHEDULE EVERY 1 MONTH STARTS '2025-11-01 17:46:07' ON COMPLETION NOT PRESERVE ENABLE DO INSERT INTO mantenimiento_programado(fecha, descripcion)
VALUES(NOW(), 'Revisión mensual de equipos')$$

DELIMITER ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
