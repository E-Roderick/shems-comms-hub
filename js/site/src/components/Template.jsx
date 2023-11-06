import SideBar from "./SideBar";

export default function Template(props) {
    return (
        <>
            <SideBar />
            <>{props.children}</>
        </>
    )
}
