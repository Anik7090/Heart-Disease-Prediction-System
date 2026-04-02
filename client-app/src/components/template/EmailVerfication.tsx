import {
  Body,
  Container,
  Head,
  Html,
  Link,
  Preview,
  Section,
  Text,
} from "@react-email/components";
import * as React from "react";

interface EmailVerifyProps {
  verifyCode: string;
}

// const baseUrl = process.env.VERCEL_URL
//   ? `https://${process.env.VERCEL_URL}`
//   : "";

export const EmailVerify = ({ verifyCode }: EmailVerifyProps) => (
  <Html>
    <Head />
    <Body style={main}>
      <Preview>
        A fine-grained personal access token has been added to your account
      </Preview>
      <Container style={container}>
        <Text style={title}>
          A one-time-password was created on your account. Do not share to
          anyone
        </Text>

        <Section style={section}>
          <Text style={text}>Valid for 10 minutes</Text>
          <Text style={text}>One Time Password</Text>
          <code>
            {verifyCode.split("").map((char, index) => (
              <span key={index} style={{ marginRight: "4px" }}>
                {char}
              </span>
            ))}
          </code>
        </Section>
        <Text style={links}>
          <Link style={link}>Your security audit log</Link>
          <Link style={link}>Contact support</Link>
        </Text>

        <Text style={footer}>
          GitHub, Inc. ・88 Colin P Kelly Jr Street ・San Francisco, CA 94107
        </Text>
      </Container>
    </Body>
  </Html>
);

export default EmailVerify;

const main = {
  backgroundColor: "#ffffff",
  color: "#24292e",
  fontFamily:
    '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji"',
};

const container = {
  maxWidth: "480px",
  margin: "0 auto",
  padding: "20px 0 48px",
};

const title = {
  fontSize: "24px",
  lineHeight: 1.25,
};

const section = {
  padding: "24px",
  border: "solid 1px #dedede",
  borderRadius: "5px",
  textAlign: "center" as const,
};

const text = {
  margin: "0 0 10px 0",
  textAlign: "left" as const,
};

// const button = {
//   fontSize: "14px",
//   backgroundColor: "#28a745",
//   color: "#fff",
//   lineHeight: 1.5,
//   borderRadius: "0.5em",
//   padding: "12px 24px",
// };

const links = {
  textAlign: "center" as const,
};

const link = {
  color: "#0366d6",
  fontSize: "12px",
};

const footer = {
  color: "#6a737d",
  fontSize: "12px",
  textAlign: "center" as const,
  marginTop: "60px",
};
