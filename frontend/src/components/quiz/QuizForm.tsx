"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Icon } from "@/components/ui";
import { ApiClientError, apiPost } from "@/lib/client";
import { t } from "@/lib/messages";
import type { Lang, QuizFull, QuizSubmitResult } from "@/lib/types";

export function QuizForm({
  quiz,
  csrf,
  lang,
}: {
  quiz: QuizFull;
  csrf: string;
  lang: Lang;
}) {
  const router = useRouter();
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const total = quiz.total;
  const answered = quiz.questions.reduce(
    (count, question) => count + (answers[question.id] === undefined ? 0 : 1),
    0
  );
  const progress = total > 0 ? Math.round((answered / total) * 100) : 0;

  function selectAnswer(questionId: string, optionIndex: number) {
    setAnswers((current) => ({ ...current, [questionId]: optionIndex }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    if (answered < total) {
      const message = t(
        lang,
        "Has respondido {answered} de {total} preguntas. ¿Enviar de todos modos?",
        { answered, total }
      );
      if (!window.confirm(message)) return;
    }

    const payload: Record<string, number | null> = {};
    for (const question of quiz.questions) {
      payload[question.id] = answers[question.id] ?? null;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await apiPost<QuizSubmitResult>(
        `/api/v1/quiz/${quiz.id}`,
        { answers: payload },
        csrf
      );
      router.push(`/quiz/intento/${result.attempt_id}`);
    } catch (caught) {
      setError(
        caught instanceof ApiClientError
          ? caught.message
          : t(lang, "El servidor no respondió. Inténtalo de nuevo.")
      );
      setSubmitting(false);
    }
  }

  return (
    <>
      <div className="quiz-progress">
        <div className="quiz-progress-row">
          <span
            aria-live="polite"
            data-quiz-answered
            data-quiz-label={t(lang, "{answered} de {total} respondidas", {
              answered: "{n}",
              total,
            })}
          >
            {t(lang, "{answered} de {total} respondidas", {
              answered,
              total,
            })}
          </span>
          <span>{t(lang, "Sin límite de tiempo")}</span>
        </div>
        <div
          className="progress"
          role="progressbar"
          aria-label={t(lang, "Progreso del quiz")}
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <span
            className="progress-bar"
            data-quiz-bar
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <form className="quiz-form" onSubmit={handleSubmit}>
        {error ? (
          <div className="flash flash-danger" role="alert">
            <Icon name="alert" />
            <span>{error}</span>
          </div>
        ) : null}

        {quiz.questions.map((question, questionIndex) => {
          const isAnswered = answers[question.id] !== undefined;
          return (
            <section
              className={`quiz-card${isAnswered ? " is-answered" : ""}`}
              id={`pregunta-${questionIndex + 1}`}
              key={question.id}
            >
              <div className="quiz-question">
                <span className="quiz-qnum">{questionIndex + 1}</span>
                <h3>{question.prompt}</h3>
              </div>
              <div className="quiz-options">
                {question.options.map((option, optionIndex) => (
                  <label
                    className="quiz-option"
                    key={`${question.id}-${optionIndex}`}
                  >
                    <input
                      type="radio"
                      name={question.id}
                      value={optionIndex}
                      checked={answers[question.id] === optionIndex}
                      onChange={() => selectAnswer(question.id, optionIndex)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </section>
          );
        })}

        <div className="quiz-actions">
          <button
            className="btn btn-primary btn-lg"
            type="submit"
            disabled={submitting}
            aria-busy={submitting}
          >
            <Icon name="send" /> {t(lang, "Enviar respuestas")}
          </button>
          <span className="small muted">
            {t(lang, "Puedes cambiar tus respuestas antes de enviar.")}
          </span>
        </div>
      </form>
    </>
  );
}
