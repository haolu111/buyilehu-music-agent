import type { ReactNode } from "react";
import { Badge, Flex, Heading, Text } from "@radix-ui/themes";

export function MusicClassroomFrame({
  kicker,
  title,
  summary,
  status = "可课堂试用",
  children,
  teacherBoundary
}: {
  kicker: string;
  title: string;
  summary: string;
  status?: string;
  children: ReactNode;
  teacherBoundary: string;
}) {
  return (
    <section className="classroom-suite-component">
      <header className="classroom-suite-component-head">
        <Flex align="center" justify="between" gap="3" wrap="wrap">
          <div>
            <Text as="p" size="2" weight="bold" color="teal">{kicker}</Text>
            <Heading as="h2" size="7">{title}</Heading>
          </div>
          <Badge color="green" variant="soft">{status}</Badge>
        </Flex>
        <Text as="p" size="3" color="gray">{summary}</Text>
      </header>
      {children}
      <footer className="classroom-teacher-boundary">
        <strong>教师专业判断边界</strong>
        <span>{teacherBoundary}</span>
      </footer>
    </section>
  );
}
