"use client";
import { useState, FormEvent } from "react";
import { z } from "zod";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const FormDataSchema = z.object({
    user_email: z.string().email(),
  });

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const formDataJson: object = {};

    for (const [key, value] of formData.entries()) {
      formDataJson[key] = value;
    }

    const formDataValidation = FormDataSchema.safeParse(formDataJson);
    if (!formDataValidation.success) {
      const error = formDataValidation.error.issues[0];
      setError(error.path[0] + ": " + error.message);
    } else {
      await fetch(
        process.env.NEXT_PUBLIC_API_HOST +
          "/user/auth/forgot_password?" +
          new URLSearchParams({
            user_email: formDataJson.user_email,
          }),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        },
      ).then((res) => {
        if (res.status == 200) {
          router.push("/password/new?user_email=" + formDataJson.user_email);
        } else {
          setError("Server processing error, please retry later!");
        }
      });
    }
  }

  return (
    <>
      <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <img
            className="mx-auto h-28 w-28 rounded-2xl"
            src="/logo.png"
            alt="PDF GPT"
          />
          {error && (
            <div
              role="alert"
              className="alert alert-error shrink w-auto h-14 mx-auto mt-2"
              onClick={() => {
                setError(null);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="stroke-current shrink-0 h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}
          <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-slate-50">
            Password Reset
          </h2>
        </div>

        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form className="space-y-6" onSubmit={onSubmit}>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium leading-6 text-slate-50"
              >
                Email address
              </label>
              <div className="mt-2">
                <input
                  id="user_email"
                  name="user_email"
                  type="email"
                  autoComplete="email"
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-slate-50 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Send OTP
              </button>
            </div>
          </form>

          <p className="mt-10 text-center text-sm text-gray-500 text-lg">
            Not a member?{" "}
            <a
              href="/register"
              className="mx-2 font-semibold leading-6 text-indigo-600 hover:text-indigo-500"
            >
              Register
            </a>
          </p>
        </div>
      </div>
    </>
  );
}
