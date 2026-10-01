CREATE TABLE `daily_logs` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `placement_id` int(11) NOT NULL,
  `log_date` date NOT NULL,
  `sign_in_time` time DEFAULT NULL,
  `sign_in_latitude` decimal(10,8) DEFAULT NULL,
  `sign_in_longitude` decimal(11,8) DEFAULT NULL,
  `sign_out_time` time DEFAULT NULL,
  `sign_out_latitude` decimal(10,8) DEFAULT NULL,
  `sign_out_longitude` decimal(11,8) DEFAULT NULL,
  `activity` text NOT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `status` varchar(30) DEFAULT 'PENDING'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `daily_logs` (`id`, `student_id`, `placement_id`, `log_date`, `sign_in_time`, `sign_in_latitude`, `sign_in_longitude`, `sign_out_time`, `sign_out_latitude`, `sign_out_longitude`, `activity`, `attachment`, `status`) VALUES
(3, 1, 1, '2026-09-03', '08:00:00', -6.16590000, 39.20260000, '17:00:00', -6.16500000, 39.20200000, 'Worked on backend development', NULL, 'PENDING');

CREATE TABLE `log_reviews` (
  `id` int(11) NOT NULL,
  `log_id` int(11) NOT NULL,
  `supervisor_id` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `decision` varchar(30) DEFAULT NULL,
  `reviewed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `organizations` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `contact_phone` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `organizations` (`id`, `name`, `address`, `contact_person`, `contact_phone`) VALUES
(1, 'SUZA', 'Zanzibar', 'Field Training Coordinator', '0000000000'),
(2, 'Test Organization', 'Zanzibar', 'John Supervisor', '0712345678');

CREATE TABLE `placements` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `organization_id` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(30) DEFAULT 'ACTIVE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `placements` (`id`, `student_id`, `organization_id`, `start_date`, `end_date`, `status`) VALUES
(1, 1, 1, '2026-09-03', '2026-12-03', 'ACTIVE'),
(2, 1, 1, '2026-09-03', '2026-12-03', 'ACTIVE');

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `placement_id` int(11) NOT NULL,
  `report_type` varchar(50) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `supervisor_assignment` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `supervisor_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `supervisor_assignment` (`id`, `student_id`, `supervisor_id`) VALUES
(1, 1, 2),
(2, 1, 2);

CREATE TABLE `supervisor_assignments` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `supervisor_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `institutional_id` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `programme` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('STUDENT','FIELD_SUPERVISOR','ACADEMIC_SUPERVISOR','COORDINATOR','ADMIN') NOT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `users` (`id`, `institutional_id`, `name`, `email`, `programme`, `password`, `role`, `status`, `created_at`, `updated_at`) VALUES
(1, 'TEST001', 'Test Student', 'test001@example.com', 'IT with Accounting', 'scrypt:32768:8:1$EnKXv3xO6TLYv6oG$bdb37f9fb6b9672cdd04da8eb7f9c41d3dbec355605749ff6a66a3b9eb37feddbf924cc22cd3a14c82c6e1193c54264cf7a262f91181d835b192fd9791ec1417', 'STUDENT', 'ACTIVE', '2026-09-02 12:02:09', '2026-09-02 12:02:09'),
(2, 'SUP001', 'Test Field Supervisor', 'supervisor@example.com', 'Information Technology', '123456', 'FIELD_SUPERVISOR', 'ACTIVE', '2026-09-07 07:15:34', '2026-09-07 07:15:34');

ALTER TABLE `daily_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `placement_id` (`placement_id`);

ALTER TABLE `log_reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `log_id` (`log_id`),
  ADD KEY `supervisor_id` (`supervisor_id`);

ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `organizations`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `placements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `organization_id` (`organization_id`);

ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `placement_id` (`placement_id`);

ALTER TABLE `supervisor_assignment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `supervisor_id` (`supervisor_id`);

ALTER TABLE `supervisor_assignments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `supervisor_id` (`supervisor_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `institutional_id` (`institutional_id`),
  ADD UNIQUE KEY `email` (`email`);

ALTER TABLE `daily_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

ALTER TABLE `log_reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `organizations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `placements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `supervisor_assignment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `supervisor_assignments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

ALTER TABLE `daily_logs`
  ADD CONSTRAINT `daily_logs_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `daily_logs_ibfk_2` FOREIGN KEY (`placement_id`) REFERENCES `placements` (`id`);

ALTER TABLE `log_reviews`
  ADD CONSTRAINT `log_reviews_ibfk_1` FOREIGN KEY (`log_id`) REFERENCES `daily_logs` (`id`),
  ADD CONSTRAINT `log_reviews_ibfk_2` FOREIGN KEY (`supervisor_id`) REFERENCES `users` (`id`);

ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `placements`
  ADD CONSTRAINT `placements_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `placements_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`);

ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`placement_id`) REFERENCES `placements` (`id`);

ALTER TABLE `supervisor_assignment`
  ADD CONSTRAINT `supervisor_assignment_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `supervisor_assignment_ibfk_2` FOREIGN KEY (`supervisor_id`) REFERENCES `users` (`id`);

ALTER TABLE `supervisor_assignments`
  ADD CONSTRAINT `supervisor_assignments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `supervisor_assignments_ibfk_2` FOREIGN KEY (`supervisor_id`) REFERENCES `users` (`id`);

COMMIT;
