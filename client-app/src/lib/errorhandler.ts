export const errorHandler = (
  error: unknown,
  defaultMessage?: string
): { success: boolean; message?: string } => {
  let message = defaultMessage ?? "Something went wrong";
  if (error instanceof Error) message = error.message;
  return { success: false, message };
};
