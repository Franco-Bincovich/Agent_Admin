'use client';

import { useState } from 'react';

function validateEmail(v: string): string {
  if (!v) return 'El email es obligatorio';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))
    return 'Ingresá un email con el formato nombre@empresa.com';
  return '';
}

function validatePassword(v: string): string {
  if (!v) return 'La contraseña es obligatoria';
  if (v.length < 8) return 'La contraseña tiene que tener al menos 8 caracteres';
  return '';
}

interface LoginFormResult {
  email: string;
  password: string;
  emailError: string;
  passwordError: string;
  isFormValid: boolean;
  handleEmailChange: (value: string) => void;
  handlePasswordChange: (value: string) => void;
  handleBlur: (field: 'email' | 'password') => void;
  validateAll: () => boolean;
}

export function useLoginForm(): LoginFormResult {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [touched, setTouched] = useState({ email: false, password: false });

  const isFormValid = !validateEmail(email) && !validatePassword(password);

  function handleEmailChange(value: string) {
    setEmail(value);
    if (touched.email) setEmailError(validateEmail(value));
  }

  function handlePasswordChange(value: string) {
    setPassword(value);
    if (touched.password) setPasswordError(validatePassword(value));
  }

  function handleBlur(field: 'email' | 'password') {
    setTouched((prev) => ({ ...prev, [field]: true }));
    if (field === 'email') setEmailError(validateEmail(email));
    if (field === 'password') setPasswordError(validatePassword(password));
  }

  function validateAll(): boolean {
    const eErr = validateEmail(email);
    const pErr = validatePassword(password);
    setEmailError(eErr);
    setPasswordError(pErr);
    setTouched({ email: true, password: true });
    return !eErr && !pErr;
  }

  return {
    email, password,
    emailError, passwordError,
    isFormValid,
    handleEmailChange, handlePasswordChange, handleBlur,
    validateAll,
  };
}
