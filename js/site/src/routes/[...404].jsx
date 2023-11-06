import { Title } from "solid-start";
import { HttpStatusCode } from "solid-start/server";
import Page from "~/components/Page";
export default function NotFound() {
  return (

      <Page title={"Error: 404"} heading={"Page not Found"} >
        <Title>Not Found</Title>
        <HttpStatusCode code={404} />
        <p>The request page could not be found.</p>
      </Page>
  );
}
