'use client';

import { useState } from 'react';

function validateUsername(v: string): string {
  if (!v) return 'El usuario es obligatorio';
  if (v.length < 3) return 'El usuario tiene que tener al menos 3 caracteres';
  return '';
}

function validatePassword(v: string): string {
  if (!v) return 'La contraseña es obligatoria';
  if (v.length < 8) return 'La contraseña tiene que tener al menos 8 caracteres';
  return '';
}

interface LoginFormResult {
  username: string;
  password: string;
  usernameError: string;
  passwordError: string;
  isFormValid: boolean;
  handleUsernameChange: (value: string) => void;
  handlePasswordChange: (value: string) => void;
  handleBlur: (field: 'username' | 'password') => void;
  validateAll: () => boolean;
}

export function useLoginForm(): LoginFormResult {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [touched, setTouched] = useState({ username: false, password: false });

  const isFormValid = !validateUsername(username) && !validatePassword(password);

  function handleUsernameChange(value: string) {
    setUsername(value);
    if (touched.username) setUsernameError(validateUsername(value));
  }

  function handlePasswordChange(value: string) {
    setPassword(value);
    if (touched.password) setPasswordError(validatePassword(value));
  }

  function handleBlur(field: 'username' | 'password') {
    setTouched((prev) => ({ ...prev, [field]: true }));
    if (field === 'username') setUsernameError(validateUsername(username));
    if (field === 'password') setPasswordError(validatePassword(password));
  }

  function validateAll(): boolean {
    const uErr = validateUsername(username);
    const pErr = validatePassword(password);
    setUsernameError(uErr);
    setPasswordError(pErr);
    setTouched({ username: true, password: true });
    return !uErr && !pErr;
  }

  return {
    username, password,
    usernameError, passwordError,
    isFormValid,
    handleUsernameChange, handlePasswordChange, handleBlur,
    validateAll,
  };
}
