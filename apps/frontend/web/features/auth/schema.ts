import { z } from "zod";

export const loginSchema = z.object({

  email: z
    .string()
    .email("Enter a valid email address"),

  password: z
    .string()
    .min(
      8,
      "Password must be at least 8 characters"
    ),

});

export type LoginForm = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  email: z
    .email("Enter a valid email address"),

  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password cannot exceed 128 characters"),

  username: z
    .string()
    .min(3, "Username must be at least 3 characters")
    .max(50, "Username cannot exceed 50 characters")
    .optional(),

  full_name: z
    .string()
    .max(100, "Full name cannot exceed 100 characters")
    .optional(),

  accept_terms: z
    .boolean()
    .refine(
      (value) => value === true,
      {
        message: "You must accept the terms and conditions",
      }
    ),
});

export type RegisterForm = z.infer<typeof registerSchema>;